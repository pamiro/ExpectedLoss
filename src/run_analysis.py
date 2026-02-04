import sys
import os
from datetime import date

# Ensure root and src are in path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Try importing real PySpark; if it fails (or later on execution), use Mock
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import DoubleType, StringType, IntegerType, StructType, StructField
    USE_MOCK = False
except ImportError:
    USE_MOCK = True

from src.data_model import DataGenerator, IFRS9Schema
from src.pd_pit_model import PDPITModel
from src.transition_matrix import TransitionMatrixModel
from src.ecl_engine import ECLEngine

if USE_MOCK:
    from src.mock_spark import SparkSession, F
    # Mock Types
    def DoubleType(): return "double"
    def StringType(): return "string"
    def IntegerType(): return "int"
    class StructField:
        def __init__(self, name, *args): self.name=name
    class StructType:
        def __init__(self, fields): self.names = [f.name for f in fields]

def run_analysis():
    # 1. Initialize Spark (Mock or Real)
    try:
        if USE_MOCK: raise Exception("Force Mock")
        spark = SparkSession.builder.appName("IFRS9_Analysis_Runner").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        # Test basic DF creation to see if winutils fails immediately
        spark.createDataFrame([{"a":1}]).show()
    except Exception as e:
        print(f"Warning: Spark initialization failed ({e}). Switching to MockSpark.")
        from src.mock_spark import SparkSession, F
        spark = SparkSession.builder.appName("Mock_Runner").getOrCreate()
        
        # We need to monkeypath the modules to use Mock F
        import src.data_model
        import src.pd_pit_model
        import src.transition_matrix
        import src.ecl_engine
        
        src.data_model.F = F
        src.data_model.SparkSession = SparkSession
        src.pd_pit_model.F = F
        src.pd_pit_model.DataFrame = src.mock_spark.MockDataFrame
        src.transition_matrix.F = F
        src.transition_matrix.DataFrame = src.mock_spark.MockDataFrame
        src.ecl_engine.F = F
        src.ecl_engine.DataFrame = src.mock_spark.MockDataFrame
        src.ecl_engine.Window = src.mock_spark.Window

    
    print(">>> [1/5] Generating Synthetic Data...")
    gen = DataGenerator(spark)
    start_date = date(2023, 1, 1)
    
    # Generate 5 Years of Macro Forecast
    macro_df = gen.generate_macro_data(start_date, years=5)
    
    # Generate Portfolio (Snapshot at start_date)
    # We only need the snapshot to project forward, but the generator makes history.
    # We'll take the 'current' state.
    portfolio_df_full = gen.generate_portfolio_data(start_date, num_obligors=100, years=1)
    portfolio_current = portfolio_df_full.filter(F.col(IFRS9Schema.DATE) == start_date)
    
    if portfolio_current.count() == 0:
        # Fallback if specific date empty, take first available date
        first_date = portfolio_df_full.select(F.min(IFRS9Schema.DATE)).collect()[0][0]
        portfolio_current = portfolio_df_full.filter(F.col(IFRS9Schema.DATE) == first_date)
        
    print(f"    Portfolio Size: {portfolio_current.count()} obligors")

    print(">>> [2/5] Initializing Models...")
    # PIT Model for Z-Factor calculation
    pit_model = PDPITModel(rho=0.15)
    
    # Transition Matrix Model
    # Define generic Rating Grades corresponding to our segments/risk?
    # For this simplified run, we assume the internal_rating maps to these.
    ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "Default"]
    tm_model = TransitionMatrixModel(ratings)
    
    # Hardcoded Base TTC Matrix (Diagonal-heavy)
    # 8x8 Identity-like
    n_states = len(ratings)
    ttc_matrix = [[0.0]*n_states for _ in range(n_states)]
    for i in range(n_states):
        if i == n_states - 1: # Default
            ttc_matrix[i][i] = 1.0
        else:
            ttc_matrix[i][i] = 0.90
            if i < n_states - 1: ttc_matrix[i][i+1] = 0.09 # Downgrade
            if i > 0: ttc_matrix[i][i-1] = 0.01 # Upgrade (simplified)
            # Normalize remainder to Default?
            remainder = 1.0 - sum(ttc_matrix[i])
            ttc_matrix[i][n_states-1] += remainder

    print(">>> [3/5] Projecting PDs & LGDs (Transition Matrix + PIT)...")
    
    # We need to project for each Scenario and each Month (or Year)
    # Scenarios: Base, Optimistic, Pessimistic
    scenarios = ["Base", "Optimistic", "Pessimistic"]
    projection_horizon_months = 36 # 3 Years
    
    # Pre-calculate Z-factors for all macro data
    macro_z = pit_model._calculate_z_factor(macro_df).cache()
    
    projections_data = []
    
    # To avoid iterating 100 obligors x 3 scenarios x 36 months in Python (too slow),
    # we will do a "Representative Portfolio" approach or Vectorized approach.
    # For specific obligors, we need their starting Rating.
    # Let's map Portfolio PD to a Rating Index bucket.
    
    # Assign Rating Index based on PD (Proxy)
    # PD < 0.001 -> AAA (0), ... > 0.1 -> CCC (6), Default (7)
    portfolio_scored = portfolio_current.withColumn(
        "rating_idx",
        F.when(F.col(IFRS9Schema.PD) < 0.0005, 0)
         .when(F.col(IFRS9Schema.PD) < 0.001, 1)
         .when(F.col(IFRS9Schema.PD) < 0.005, 2)
         .when(F.col(IFRS9Schema.PD) < 0.01, 3)
         .when(F.col(IFRS9Schema.PD) < 0.02, 4)
         .when(F.col(IFRS9Schema.PD) < 0.05, 5)
         .when(F.col(IFRS9Schema.STAGE) == 3, 7) # Default
         .otherwise(6) # CCC
    ).cache()
    
    # Collect generic obligor info (ID, Rating, EAD, LGD, Stage)
    obligor_list = portfolio_scored.select(
        IFRS9Schema.OBLIGOR_ID, "rating_idx", IFRS9Schema.LGD, IFRS9Schema.EAD, IFRS9Schema.STAGE, IFRS9Schema.INTEREST_RATE
    ).collect()

    # Pre-compute Cumulative PD Curves for each Scenario/Rating
    # Map: Scenario -> [Year1_Z, Year2_Z, Year3_Z...]
    # We'll take average Z per year from macro
    z_per_scenario = {}
    for scen in scenarios:
        # Get avg Z for first 3 years
        # Filter scenario
        scen_rows = macro_z.filter(F.col(IFRS9Schema.SCENARIO) == scen).orderBy(IFRS9Schema.DATE).collect()
        
        # Aggregate monthly Z to yearly Z (simplified)
        yearly_z = []
        for y in range(3):
            # Take months y*12 to (y+1)*12
            start_idx = y*12
            end_idx = min((y+1)*12, len(scen_rows))
            if start_idx < len(scen_rows):
                subset = scen_rows[start_idx:end_idx]
                avg_z = sum([r['Z_Factor'] for r in subset]) / len(subset) if subset else 0.0
                yearly_z.append(avg_z)
            else:
                yearly_z.append(0.0)
        z_per_scenario[scen] = yearly_z

    # Build Cumulative PDs and Marginal PDs logic
    # Curve Map: (Scenario, Rating_Idx) -> [Marginal_PD_Month_1 ... Month_36]
    pd_curves = {}
    
    for scen, z_list in z_per_scenario.items():
        # Calculate Chain of Matrices
        matrices_yearly = []
        cumulative_matrix = None
        
        # Calculate yearly matrices
        for z in z_list:
            m_pit = tm_model.condition_matrix(ttc_matrix, z_factor=z, rho=0.15)
            matrices_yearly.append(m_pit)
            
        # We need MONTHLY Marginal PDs.
        # Approximation: Linear interpolation of Cumulative PDs between years?
        # Or better: Assume constant matrix for the year M^(1/12). 
        # Simplified: We treat the "yearly" matrix as applicable for the year, 
        # but we need marginal Step.
        # Let's compute Cumulative PD at Year 1, Year 2, Year 3.
        
        cum_pd_points = {} # Rating -> [PD_Y1, PD_Y2, PD_Y3]
        
        # Calc cumulative matrices
        m_cum = None
        m_cum_list = []
        for m in matrices_yearly:
            if m_cum is None: m_cum = m
            else: m_cum = tm_model.multiply_matrices(m_cum, m)
            m_cum_list.append(m_cum)
            
        for r_idx in range(n_states):
            curve = tm_model.get_cumulative_pd_curve(r_idx, m_cum_list)
            # curve is [PD_1yr, PD_2yr, PD_3yr]
            cum_pd_points[r_idx] = [0.0] + curve # Start at 0
            
        # Interpolate to Monthly Marginal
        for r_idx in range(n_states):
            marginal_pds = []
            yr_points = cum_pd_points[r_idx]
            for y in range(3):
                start_pd = yr_points[y]
                end_pd = yr_points[y+1]
                # Distribute (End - Start) over 12 months
                monthly_marginal = max(0.0, end_pd - start_pd) / 12.0
                marginal_pds.extend([monthly_marginal]*12)
            pd_curves[(scen, r_idx)] = marginal_pds

    # Expand Obligors
    for obs in obligor_list:
        r_idx = obs['rating_idx']
        
        # If already default, PD is 1.0 immediately? Or 0 marginal?
        # If Default, ECL is LGD * EAD.
        # Let's handle performing only for dynamic PDs.
        
        for scen in scenarios:
            curve = pd_curves.get((scen, r_idx), [0.0]*36)
            
            for t_idx, pd_marg in enumerate(curve):
                month = t_idx + 1
                if obs[IFRS9Schema.STAGE] == 3:
                     # Already default
                     pd_real = 1.0 if month == 1 else 0.0
                else:
                     pd_real = pd_marg
                
                projections_data.append((
                    obs[IFRS9Schema.OBLIGOR_ID],
                    scen,
                    month,
                    float(pd_real),
                    float(obs[IFRS9Schema.LGD]), # Simplified constant LGD
                    float(obs[IFRS9Schema.EAD]), # Simplified constant EAD
                    float(obs[IFRS9Schema.INTEREST_RATE]),
                    int(obs[IFRS9Schema.STAGE])
                ))
                
    # Create Spark DF
    proj_schema = StructType([
        StructField("obligor_id", StringType(), True),
        StructField("scenario", StringType(), True),
        StructField("month_idx", IntegerType(), True),
        StructField("pd_marginal", DoubleType(), True),
        StructField("lgd", DoubleType(), True),
        StructField("ead", DoubleType(), True),
        StructField("interest_rate", DoubleType(), True),
        StructField("stage", IntegerType(), True)
    ])
    
    # Batch create to avoid overhead? 100 obligors * 3 scen * 36 months = ~10k rows. Fine.
    projections_df = spark.createDataFrame(projections_data, proj_schema)

    print(">>> [4/5] Calculating ECL...")
    engine = ECLEngine()
    ecl_scenarios = engine.calculate_ecl(projections_df)
    final_ecl = engine.aggregate_scenarios(ecl_scenarios)
    
    # Collect Results for Reporting
    results = final_ecl.join(portfolio_scored, on=IFRS9Schema.OBLIGOR_ID).collect()
    
    # Also collect aggregates by Scenario
    ecl_by_scenario = ecl_scenarios.groupBy(IFRS9Schema.SCENARIO).agg(F.sum("ECL_Scenario").alias("Total_ECL")).collect()
    
    print(">>> [5/5] Generating Report...")
    generate_report(results, ecl_by_scenario)
    
    spark.stop()

def generate_report(obligor_results, scenario_results):
    """Generates a text/markdown report."""
    
    total_ecl = sum([row['Final_ECL'] for row in obligor_results])
    total_ead = sum([row[IFRS9Schema.EAD] for row in obligor_results])
    coverage_ratio = (total_ecl / total_ead) * 100 if total_ead > 0 else 0
    
    # Scenario Impact
    scen_map = {row['scenario']: row['Total_ECL'] for row in scenario_results}
    base_ecl = scen_map.get('Base', 0)
    pess_ecl = scen_map.get('Pessimistic', 0)
    impact_pct = ((pess_ecl - base_ecl) / base_ecl) * 100 if base_ecl > 0 else 0
    
    # Stage Breakdown
    stage_1_ecl = sum([row['Final_ECL'] for row in obligor_results if row[IFRS9Schema.STAGE] == 1])
    stage_2_ecl = sum([row['Final_ECL'] for row in obligor_results if row[IFRS9Schema.STAGE] == 2])
    stage_3_ecl = sum([row['Final_ECL'] for row in obligor_results if row[IFRS9Schema.STAGE] == 3])
    
    def safe_pct(num, den):
        return (num / den) * 100 if den > 0 else 0.0

    report_content = f"""# IFRS 9 ECL Analysis Report

## Executive Summary
**Total ECL**: €{total_ecl:,.2f}
**Total Exposure**: €{total_ead:,.2f}
**Coverage Ratio**: {coverage_ratio:.2f}%

---

## 1. Scenario Analysis (Sensitivity)
The impact of the Pessimistic Scenario compared to Base Case:

| Scenario | Total ECL (€) | Δ vs Base |
| :--- | :--- | :--- |
| **Base** | €{base_ecl:,.2f} | - |
| **Optimistic** | €{scen_map.get('Optimistic', 0):,.2f} | {safe_pct(scen_map.get('Optimistic',0)-base_ecl, base_ecl):.1f}% |
| **Pessimistic** | €{pess_ecl:,.2f} | **{impact_pct:+.1f}%** |

> [!WARNING]
> The Pessimistic scenario drives a {impact_pct:.1f}% increase in provisions, highlighting sensitivity to Example macro factors (Z-Factor).

---

## 2. Stage Breakdown (Staging)

| Stage | Definition | ECL Amount (€) | % of Total |
| :--- | :--- | :--- | :--- |
| **Stage 1** | Performing (12m ECL) | €{stage_1_ecl:,.2f} | {safe_pct(stage_1_ecl, total_ecl):.1f}% |
| **Stage 2** | Underperforming (Lifetime) | €{stage_2_ecl:,.2f} | {safe_pct(stage_2_ecl, total_ecl):.1f}% |
| **Stage 3** | Defaulted (Lifetime) | €{stage_3_ecl:,.2f} | {safe_pct(stage_3_ecl, total_ecl):.1f}% |

"""
    
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Report generated: analysis_report.md")

if __name__ == "__main__":
    run_analysis()
