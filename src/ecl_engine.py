from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, DoubleType

# Depending on how the user runs this, import might need adjustment
try:
    from data_model import IFRS9Schema
except ImportError:
    from src.data_model import IFRS9Schema

class ECLEngine:
    """
    Calculates Expected Credit Loss (ECL) under IFRS 9 / CECL.
    ECL = Sum(PD_t * LGD_t * EAD_t * DiscountFactor_t)
    Weights multiple scenarios.
    """
    
    def __init__(self, scenario_weights: dict = None):
        """
        :param scenario_weights: Dictionary of Scenario Name -> Probability.
                                 Default: Base=0.4, Optimistic=0.3, Pessimistic=0.3
        """
        if scenario_weights is None:
            self.scenario_weights = {
                "Base": 0.4,
                "Optimistic": 0.3,
                "Pessimistic": 0.3
            }
        else:
            self.scenario_weights = scenario_weights

    def calculate_ecl(self, projections_df: DataFrame) -> DataFrame:
        """
        Calculates Stage 1 (12m) and Lifetime ECL for each obligor/scenario.
        
        Expected Input Schema (projections_df):
        - obligor_id
        - scenario
        - month_idx (1, 2, ... T)
        - pd_marginal (Probability of defaulting specifically in month t)
        - lgd (expected LGD in month t)
        - ead (expected EAD in month t)
        - interest_rate (EIR for discounting)
        - stage (Current Stage of the obligor, constant for the projection usually)
        """
        
        # 1. Calculate Discount Factor
        # DF_t = 1 / (1 + EIR/12)^t 
        # (Assuming monthly steps)
        df_calc = projections_df.withColumn(
            "discount_factor", 
            1.0 / F.pow(1.0 + F.col(IFRS9Schema.INTEREST_RATE)/12.0, F.col("month_idx"))
        )
        
        # 2. Calculate Monthly ECL Component
        # ecl_t = PD_marginal_t * LGD_t * EAD_t * DF_t
        df_calc = df_calc.withColumn(
            "ecl_component",
            F.col("pd_marginal") * F.col(IFRS9Schema.LGD) * F.col(IFRS9Schema.EAD) * F.col("discount_factor")
        )
        
        # 3. Aggregate 12-Month and Lifetime ECL per Obligor/Scenario
        # Window by Obligor + Scenario
        w = Window.partitionBy(IFRS9Schema.OBLIGOR_ID, IFRS9Schema.SCENARIO)
        
        # 12-Month ECL: Sum of components where month_idx <= 12
        # Lifetime ECL: Sum of all components
        
        ecl_aggregated = df_calc.groupBy(IFRS9Schema.OBLIGOR_ID, IFRS9Schema.SCENARIO, IFRS9Schema.STAGE).agg(
            F.sum(F.when(F.col("month_idx") <= 12, F.col("ecl_component")).otherwise(0.0)).alias("ECL_12m"),
            F.sum("ecl_component").alias("ECL_Lifetime")
        )
        
        # 4. Determine Final ECL based on Stage
        # Stage 1 -> 12m ECL
        # Stage 2/3 -> Lifetime ECL
        ecl_final = ecl_aggregated.withColumn(
            "ECL_Scenario",
            F.when(F.col(IFRS9Schema.STAGE) == 1, F.col("ECL_12m"))
             .otherwise(F.col("ECL_Lifetime"))
        )
        
        return ecl_final

    def aggregate_scenarios(self, ecl_scenario_df: DataFrame) -> DataFrame:
        """
        Computes the Probability Weighted ECL.
        Weighted_ECL = Sum(ECL_s * Prob_s)
        """
        # Create a mapping expression for weights
        # Use simple F.when chaining instead of F.expr for better portability (and Mock support)
        weight_expr = None
        for k, v in self.scenario_weights.items():
            if weight_expr is None:
                weight_expr = F.when(F.col(IFRS9Schema.SCENARIO) == k, v)
            else:
                weight_expr = weight_expr.when(F.col(IFRS9Schema.SCENARIO) == k, v)
        
        if weight_expr:
            weight_expr = weight_expr.otherwise(0.0)
        else:
            weight_expr = F.lit(0.0)

        df_weighted = ecl_scenario_df.withColumn("scenario_weight", weight_expr)
        
        df_weighted = df_weighted.withColumn(
            "weighted_ecl", 
            F.col("ECL_Scenario") * F.col("scenario_weight")
        )
        
        # Group by Obligor to get final number
        final_df = df_weighted.groupBy(IFRS9Schema.OBLIGOR_ID, IFRS9Schema.STAGE).agg(
            F.sum("weighted_ecl").alias("Final_ECL"),
            F.collect_list(F.struct(IFRS9Schema.SCENARIO, "ECL_Scenario")).alias("Scenario_Details")
        )
        
        return final_df

if __name__ == "__main__":
    from pyspark.sql import SparkSession
    
    try:
        spark = SparkSession.builder.appName("ECL_Engine_Example").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        
        print("1. Simulating Projection Data (Obligor Paths)...")
        # Simulate 2 obligors, 3 scenarios, 20 months
        data = []
        obligors = [
            {"id": "Obs_Stage1", "stage": 1, "eir": 0.05, "lgd": 0.4, "ead": 1000.0},
            {"id": "Obs_Stage2", "stage": 2, "eir": 0.05, "lgd": 0.4, "ead": 1000.0}
        ]
        scenarios = ["Base", "Optimistic", "Pessimistic"]
        
        for obs in obligors:
            for scen in scenarios:
                for t in range(1, 21): # 20 months
                    # Simple marginal PD curve (flat or increasing)
                    pd = 0.001 if scen == "Optimistic" else (0.002 if scen == "Base" else 0.005)
                    
                    data.append((
                        obs["id"], scen, t, pd, obs["lgd"], obs["ead"], obs["eir"], obs["stage"]
                    ))
        
        schema = ["obligor_id", "scenario", "month_idx", "pd_marginal", "lgd", "ead", "interest_rate", "stage"]
        projections_df = spark.createDataFrame(data, schema)
        
        print("2. Calculating ECL per Scenario...")
        engine = ECLEngine()
        ecl_scenarios = engine.calculate_ecl(projections_df)
        ecl_scenarios.show()
        
        print("3. Probability Weighting...")
        final_ecl = engine.aggregate_scenarios(ecl_scenarios)
        final_ecl.select("obligor_id", "stage", "Final_ECL").show()
        
    except Exception as e:
        print(f"Error: {e}")
