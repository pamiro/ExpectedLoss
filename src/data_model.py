from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType, DateType
)
from datetime import date, timedelta
import random

class IFRS9Schema:
    """Schema definitions based on setup.md"""
    
    # Portfolio Columns
    DATE = 'date'
    OBLIGOR_ID = 'obligor_id'
    SEGMENT = 'segment' # Retail, Mortgage, SME
    EAD = 'ead'
    PD = 'pd'
    LGD = 'lgd'
    STAGE = 'stage'
    DPD = 'dpd'
    APD = 'apd' # Amount Past Due
    WRITE_OFFS = 'write_offs'
    RECOVERIES = 'recoveries'
    PREPAYMENTS = 'prepayments'
    INTEREST_RATE = 'interest_rate'
    ORIGINATION_DATE = 'origination_date'
    MATURITY_DATE = 'maturity_date'
    LOAN_TYPE = 'loan_type'
    LOAN_STATUS = 'loan_status'
    COLLATERAL_TYPE = 'collateral_type'
    COLLATERAL_VALUE = 'collateral_value'
    OUTSTANDING_BALANCE = 'outstanding_balance'
    UNUSED_COMMITMENT = 'unused_commitment'
    LIMIT = 'limit'
    
    # Macro Columns
    SCENARIO = 'scenario'
    GDP_GROWTH = 'gdp_growth'
    UNEMPLOYMENT_RATE = 'unemployment_rate'
    INTEREST_RATES = 'interest_rates'
    PROPERTY_INDICES = 'property_indices'
    INFLATION = 'inflation'
    EXCHANGE_RATES = 'exchange_rates'

class DataGenerator:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def generate_macro_data(self, start_date: date, years: int = 20):
        """
        Generates 20 years of macroeconomic data (monthly).
        Includes historical data and 3 forecast scenarios (Base, Optimistic, Pessimistic).
        """
        months = years * 12
        
        # Base schema
        schema = StructType([
            StructField(IFRS9Schema.DATE, DateType(), False),
            StructField(IFRS9Schema.SCENARIO, StringType(), False),
            StructField(IFRS9Schema.GDP_GROWTH, DoubleType(), True),
            StructField(IFRS9Schema.UNEMPLOYMENT_RATE, DoubleType(), True),
            StructField(IFRS9Schema.INTEREST_RATES, DoubleType(), True),
            StructField(IFRS9Schema.PROPERTY_INDICES, DoubleType(), True),
            StructField(IFRS9Schema.INFLATION, DoubleType(), True),
            StructField(IFRS9Schema.EXCHANGE_RATES, DoubleType(), True),
        ])

        # Generate separate DataFrames for History and Scenarios (simplified simulation)
        # Using Spark range to generate rows
        df = self.spark.range(0, months).withColumn("month_idx", F.col("id"))
        
        # Calculate Date
        df = df.withColumn(
            IFRS9Schema.DATE, 
            F.expr(f"date_add(to_date('{start_date}'), cast(month_idx * 30 as int))")
        )

        # Generate Scenarios (Cross Join)
        scenarios = self.spark.createDataFrame(
            [("History",), ("Base",), ("Optimistic",), ("Pessimistic",)], 
            ["scenario_temp"]
        )
        df = df.crossJoin(scenarios).withColumnRenamed("scenario_temp", IFRS9Schema.SCENARIO)

        # Simulate Economic Variables using Random functions (Placeholder logic)
        # In a real model, this would use vector autoregression or similar
        df = df.withColumn(IFRS9Schema.GDP_GROWTH, F.rand() * 0.05) \
               .withColumn(IFRS9Schema.UNEMPLOYMENT_RATE, F.rand() * 0.1) \
               .withColumn(IFRS9Schema.INTEREST_RATES, F.rand() * 0.08) \
               .withColumn(IFRS9Schema.PROPERTY_INDICES, F.lit(100.0) + F.rand() * 50) \
               .withColumn(IFRS9Schema.INFLATION, F.rand() * 0.04) \
               .withColumn(IFRS9Schema.EXCHANGE_RATES, F.lit(1.0) + F.rand() * 0.2) \
               .drop("id", "month_idx")

        return df

    def generate_portfolio_data(self, start_date: date, num_obligors: int = 1000, years: int = 20):
        """
        Generates 20 years of portfolio data for:
        - Retail Consumer Loans
        - Private Individual Mortgages
        - SME Loans
        """
        months_total = years * 12
        
        # 1. Generate Base Obligors
        # Distribute segments
        obligors = self.spark.range(0, num_obligors) \
            .withColumn(IFRS9Schema.OBLIGOR_ID, F.concat(F.lit("AG_"), F.col("id"))) \
            .withColumn("rand_seg", F.rand()) \
            .withColumn(IFRS9Schema.SEGMENT, 
                        F.when(F.col("rand_seg") < 0.5, "Retail Consumer")
                        .when(F.col("rand_seg") < 0.8, "Mortgage")
                        .otherwise("SME")) \
            .drop("rand_seg", "id")

        # 2. Expand over Time (Cross Join with Time)
        dates = self.spark.range(0, months_total).withColumn("month_idx", F.col("id")) \
            .withColumn(IFRS9Schema.DATE, 
                        F.expr(f"date_add(to_date('{start_date}'), cast(month_idx * 30 as int))")) \
            .drop("id")
            
        portfolio = obligors.crossJoin(dates)
        
        # 3. Simulate Fields based on Segment
        # Logic: 
        # - EAD/Limit depends on Segment
        # - PD/LGD are stochastic
        # - Dates are derived
        
        portfolio = portfolio.withColumn(
            IFRS9Schema.LIMIT,
            F.when(F.col(IFRS9Schema.SEGMENT) == "Retail Consumer", F.rand() * 10000 + 1000)
             .when(F.col(IFRS9Schema.SEGMENT) == "Mortgage", F.rand() * 500000 + 100000)
             .otherwise(F.rand() * 1000000 + 50000) # SME
        )
        
        # EAD usually <= Limit
        portfolio = portfolio.withColumn(
            IFRS9Schema.EAD, 
            F.col(IFRS9Schema.LIMIT) * (F.lit(0.5) + F.rand() * 0.5)
        )

        portfolio = portfolio.withColumn(IFRS9Schema.OUTSTANDING_BALANCE, F.col(IFRS9Schema.EAD))
        
        # Unused Commitment = Limit - EAD
        portfolio = portfolio.withColumn(
            IFRS9Schema.UNUSED_COMMITMENT,
            F.col(IFRS9Schema.LIMIT) - F.col(IFRS9Schema.EAD)
        )

        # Risk Components
        portfolio = portfolio.withColumn(IFRS9Schema.PD, F.rand() * 0.1) # 0-10% PD
        portfolio = portfolio.withColumn(IFRS9Schema.LGD, F.rand() * 0.6) # 0-60% LGD
        
        # Stage (Mostly 1, some 2 and 3)
        portfolio = portfolio.withColumn("rand_stage", F.rand()) \
            .withColumn(IFRS9Schema.STAGE,
                        F.when(F.col("rand_stage") < 0.9, 1)
                        .when(F.col("rand_stage") < 0.98, 2)
                        .otherwise(3)) \
            .drop("rand_stage")

        # DPD & APD (Linked to Stage somewhat)
        portfolio = portfolio.withColumn(
            IFRS9Schema.DPD,
            F.when(F.col(IFRS9Schema.STAGE) == 1, 0)
             .when(F.col(IFRS9Schema.STAGE) == 2, (F.rand() * 60).cast("int"))
             .otherwise((F.rand() * 365).cast("int"))
        ).withColumn(
            IFRS9Schema.APD,
            F.when(F.col(IFRS9Schema.DPD) > 0, F.col(IFRS9Schema.EAD) * 0.1).otherwise(0)
        )

        # Dates & Other fields
        portfolio = portfolio.withColumn(
            IFRS9Schema.ORIGINATION_DATE, 
            F.date_sub(F.col(IFRS9Schema.DATE), (F.rand() * 1000).cast("int"))
        ).withColumn(
            IFRS9Schema.MATURITY_DATE,
            F.date_add(F.col(IFRS9Schema.DATE), (F.rand() * 3000).cast("int"))
        ).withColumn(
            IFRS9Schema.INTEREST_RATE, F.lit(0.05) + F.rand() * 0.05
        ).withColumn(
            IFRS9Schema.LOAN_TYPE, F.lit("Standard")
        ).withColumn(
            IFRS9Schema.LOAN_STATUS, F.lit("Active")
        ).withColumn(
            IFRS9Schema.WRITE_OFFS, F.lit(0.0)
        ).withColumn(
            IFRS9Schema.RECOVERIES, F.lit(0.0)
        ).withColumn(
            IFRS9Schema.PREPAYMENTS, F.lit(0.0)
        )

        # Collateral (Only for Mortgage and some SME)
        portfolio = portfolio.withColumn(
            IFRS9Schema.COLLATERAL_TYPE,
            F.when(F.col(IFRS9Schema.SEGMENT) == "Mortgage", "Real Estate")
             .when(F.col(IFRS9Schema.SEGMENT) == "SME", "Equipment")
             .otherwise("None")
        ).withColumn(
            IFRS9Schema.COLLATERAL_VALUE,
            F.when(F.col(IFRS9Schema.SEGMENT) == "Mortgage", F.col(IFRS9Schema.LIMIT) * 1.2)
             .when(F.col(IFRS9Schema.SEGMENT) == "SME", F.col(IFRS9Schema.LIMIT) * 0.5)
             .otherwise(0)
        )

        return portfolio

if __name__ == "__main__":
    # Example usage (will not run without spark installed)
    try:
        spark = SparkSession.builder.appName("IFRS9DataGen").getOrCreate()
        generator = DataGenerator(spark)
        
        start_date = date(2005, 1, 1)
        
        print("Generating Macro Data...")
        macro_df = generator.generate_macro_data(start_date)
        macro_df.show()
        
        print("Generating Portfolio Data...")
        portfolio_df = generator.generate_portfolio_data(start_date, num_obligors=100)
        portfolio_df.show()
        
    except ImportError:
        print("PySpark not installed.")
    except Exception as e:
        print(f"Error: {e}")
