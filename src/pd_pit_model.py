from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
import math

# Re-importing Schema from data_model is good practice
# assuming data_model is in the same path.
try:
    from data_model import IFRS9Schema
except ImportError:
    # If running as script
    from src.data_model import IFRS9Schema

class PDPITModel:
    """
    Point-in-Time (PIT) Model fit and application.
    Uses Vasicek Single Factor Model to convert TTC PD to PIT PD.
    """

    def __init__(self, rho: float = 0.15):
        """
        :param rho: Asset Correlation factor (default 15% as per Basel corporate/retail avg)
        """
        self.rho = rho
        # Coefficients for Z-factor (Macro Index)
        # In a real model, these are fitted via Logistic Regression on Historical Default Rates
        # Here we hardcode purely for the synthesized example
        self.z_weights = {
            IFRS9Schema.GDP_GROWTH: 20.0,       # High Growth -> High Z -> Low PD (Good)
            IFRS9Schema.UNEMPLOYMENT_RATE: -10.0, # High Unemp -> Low Z -> High PD (Bad)
            IFRS9Schema.INTEREST_RATES: -5.0,     # High Rates -> Low Z -> High PD
        }
        self.z_intercept = -0.5 # Calibration offset

    def _calculate_z_factor(self, macro_df: DataFrame) -> DataFrame:
        """
        Calculates the Composite Z-Factor (Systemic Risk) from Macro Variables.
        Z should typically be N(0, 1) distributed for the Vasicek formula to hold strictly,
        so standard scaling of inputs is important.
        """
        # 1. Create Z expression
        # Z = w1*x1 + w2*x2 ... + b
        z_expr = F.lit(self.z_intercept)
        for col_name, weight in self.z_weights.items():
            if col_name in macro_df.columns:
                z_expr = z_expr + (F.col(col_name) * weight)
        
        df = macro_df.withColumn("Z_Factor", z_expr)
        return df

    def apply_vasicek_pd(self, portfolio_df: DataFrame, macro_df: DataFrame) -> DataFrame:
        """
        Applies Vasicek PIT adjustment to PD.
        formula: PIT_PD = NormalCDF( (InvNormalCDF(TTC_PD) - sqrt(rho)*Z) / sqrt(1-rho) )
        """
        # 1. Prepare Macro Data (Calculate Z)
        macro_z = self._calculate_z_factor(macro_df)
        
        # 2. Join Portfolio with Macro on Date and Scenario
        # Note: Portfolio might not have Scenario if it's actuals, but simulation data likely has it.
        # If Portfolio is just 'History', we need to match appropriately.
        # For this example, we assume portfolio_df has date, and we might cross join or map scenarios.
        
        # Checking if scenario exists in portfolio, if not, assume 'Base' or 'History'?
        # The data_model example generates a portfolio with just 'date', but macro has 'scenario'.
        # Usually, you run this function FOR a specific scenario.
        
        # Let's assume we handle a "Per Scenario" logic.
        # If macro_df has multiple scenarios, and portfolio doesn't, we will get a Cartesian join
        # which expands portfolio for each scenario (Classic IFRS9 approach).
        
        join_cols = [IFRS9Schema.DATE]
        if IFRS9Schema.SCENARIO in portfolio_df.columns:
            join_cols.append(IFRS9Schema.SCENARIO)
            
        dataset = portfolio_df.join(macro_z, on=join_cols, how='inner')

        # 3. UDFs for Normal Distribution
        # Using math.erf for CDF and a rational approximation for Inverse CDF (since numpy/scipy disallowed)
        
        # Standard Normal CDF
        @F.udf(DoubleType())
        def norm_cdf(x):
            if x is None: return 0.0
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        # Inverse Normal CDF (Acklam’s algorithm approximation)
        @F.udf(DoubleType())
        def norm_ppf(p):
            if p is None or p >= 1.0 or p <= 0.0: return 0.0
            
            # Coefficients for prediction
            a1, a2, a3, a4, a5, a6 = -3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00
            b1, b2, b3, b4, b5 = -5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01
            c1, c2, c3, c4, c5, c6 = -7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00
            d1, d2, d3, d4 = 7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00
            e1, e2, e3, e4, e5, e6 = 6.657904643501103e-03, 6.469399660036604e-01, 3.016036606598778e+02, 7.117885006608737e+03, 7.377729650203415e+04, 3.422420886858129e+05
            f1, f2, f3, f4 = 2.174396181152126e-02, 6.537337718563326e+01, 4.053259960754365e+03, 3.235543361849377e+05

            q = p - 0.5
            if abs(q) <= 0.425:
                # Central region
                r = 0.180625 - q * q
                return q * (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6) / \
                       (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1.0)
            else:
                # Tails
                r = p if q < 0 else 1.0 - p
                r = math.sqrt(-math.log(r))
                if r <= 5.0:
                    r = r - 1.6
                    val = (((((c1 * r + c2) * r + c3) * r + c4) * r + c5) * r + c6) / \
                          ((((d1 * r + d2) * r + d3) * r + d4) * r + 1.0)
                else:
                    r = r - 5.0
                    val = (((((e1 * r + e2) * r + e3) * r + e4) * r + e5) * r + e6) / \
                          ((((f1 * r + f2) * r + f3) * r + f4) * r + 1.0)
                return -val if q < 0 else val
                
        # 4. Apply Formula
        # We need to be careful with PDs close to 0 or 1.
        
        # 1/sqrt(1-rho)
        rho_factor_1 = 1.0 / math.sqrt(1.0 - self.rho)
        # sqrt(rho)/sqrt(1-rho)
        rho_factor_2 = math.sqrt(self.rho) / math.sqrt(1.0 - self.rho)
        
        dataset = dataset.withColumn("TTC_PD_Clipped", 
                            F.when(F.col(IFRS9Schema.PD) < 0.0001, 0.0001)
                             .when(F.col(IFRS9Schema.PD) > 0.9999, 0.9999)
                             .otherwise(F.col(IFRS9Schema.PD)))

        dataset = dataset.withColumn("Inv_PD", norm_ppf(F.col("TTC_PD_Clipped")))
        
        # Transformation: (InvPD - sqrt(rho)*Z) / sqrt(1-rho)
        dataset = dataset.withColumn("Distance_To_Default_PIT", 
                                     (F.col("Inv_PD") - F.col("Z_Factor") * math.sqrt(self.rho)) / math.sqrt(1 - self.rho))
        
        dataset = dataset.withColumn("PD_PIT", norm_cdf(F.col("Distance_To_Default_PIT")))
        
        # 5. Apply LGD and EAD Adjustments (Simplified scalar scalars)
        # High Z (Good Economy) -> Lower LGD
        # Formula: LGD_PIT = LGD_TTC * (1 - sensitivity * Z)
        dataset = dataset.withColumn("LGD_PIT", 
                                     F.col(IFRS9Schema.LGD) * (F.lit(1.0) - F.lit(0.05) * F.col("Z_Factor")))
        
        # EAD: Usage might increase in bad times? (Drawdown of credit lines)
        # Low Z (Bad Economy) -> Higher EAD
        dataset = dataset.withColumn("EAD_PIT",
                                     F.col(IFRS9Schema.EAD) * (F.lit(1.0) - F.lit(0.02) * F.col("Z_Factor")))
                                     
        return dataset

if __name__ == "__main__":
    from pyspark.sql import SparkSession
    from pyspark.sql import SparkSession
    from data_model import DataGenerator
    from datetime import date
    
    start_date = date(2020, 1, 1) # Standard python date object
    
    try:
        spark = SparkSession.builder.appName("IFRS9_PIT_Model").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        
        # 1. Generate Data
        print("Generating Data...")
        gen = DataGenerator(spark)
        macro_df = gen.generate_macro_data(start_date, years=5)
        portfolio_df = gen.generate_portfolio_data(start_date, num_obligors=50, years=5)
        
        # 2. Apply Model
        print("Applying PIT Model...")
        model = PDPITModel(rho=0.12)
        
        # Since portfolio generator doesn't assign scenarios, we cross join to create them
        # simulating that we iterate this portfolio through all 3 future scenarios
        scenarios = macro_df.select(IFRS9Schema.SCENARIO).distinct()
        portfolio_scenarios = portfolio_df.crossJoin(scenarios)
        
        result_df = model.apply_vasicek_pd(portfolio_scenarios, macro_df)
        
        print("Results (First 20 rows):")
        result_df.select(
            IFRS9Schema.DATE, 
            IFRS9Schema.SCENARIO,
            IFRS9Schema.PD, 
            "PD_PIT", 
            "Z_Factor"
        ).show(20)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
