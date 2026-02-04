# Setup

This file sets out some conditions for the synthesis of the python framework. The framework is in form of python package that be applied to organizational data. The parameters of the framework should be fit on organizational data. After parameters are fit, the framework should be able to generate the expected loss for the organization. The framework should be able to generate the expected loss for the organization under different scenarios. The framework should be able to generate the expected loss for the organization under different scenarios and different time horizons.

## Overlay approach

The framework requires PD, LGD and EAD to be available for each obligor. These parameters should estimated as through the cycle (TTC) or hybrid point in time (PIT) / through the cycle. 

## Portfolio focus

The framework is specialized for retail consumer loans, mortgages and SME loans. The corporate loan book is not in scope. 

## Data

That data exists in a typical organization in form of time series table. The granularity of data is set to be monthly. 
For each month there should be the following data available per obligor / facility:
- Exposure at default (EAD)
- Probability of default (PD)
- Loss given default (LGD)
- Stage (1, 2, 3)
- Days past due (DPD)
- Amount past due (APD)
- Write-offs
- Recoveries
- Prepayments
- Interest rate
- Loan origination date
- Loan maturity date
- Loan type
- Loan status
- Collateral type
- Collateral value
- Outstanding balance
- Unused commitment
- Limit

## Macroeconomic data

Macroeconomic data should be supplied in form of tables per scenario. The tables should contain the following data:
- GDP Growth
- Unemployment Rate
- Interest Rates
- Property Price Indices (for collateral)
- Inflation
- Exchange Rates

The time horizon of the macroeconomic data should be at least 10 years. The data should be supplied in form of monthly data. There should be historical data and forecast data. The forecast data should be supplied for 3 scenarios: base, optimistic and pessimistic.

## Frameworks to be used 

Pyspark should be used for the framework. No pandas or numpy should be used.


