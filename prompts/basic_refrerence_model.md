# IFRS9 Reference Model & Methodology

## 1. Regulatory Framework Analysis

### 1.1 IFRS 9 Requirements
The model is designed to comply with **IFRS 9 Financial Instruments**, specifically the impairment requirements for measuring Expected Credit Losses (ECL).

*   **Three-Stage Model**:
    *   **Stage 1 (Performing)**: 12-month ECL. Financial instruments that have not deteriorated significantly in credit quality since initial recognition.
    *   **Stage 2 (Underperforming)**: Lifetime ECL. Financial instruments that have experienced a **Significant Increase in Credit Risk (SICR)**.
    *   **Stage 3 (Non-Performing)**: Lifetime ECL. Financial instruments that are credit-impaired.

*   **Forward-Looking Information**: The model incorporates macroeconomic scenarios (Base, Optimistic, Pessimistic) to adjust PD, LGD, and EAD estimates.

### 1.2 ECB Guidelines
The model adheres to the **ECB Guide to Internal Models** and specific IFRS 9 supervisory expectations.

*   **Period of Historical Data**: Minimum 5-7 years for calibration to ensure a full economic cycle is captured.
*   **Validation**: Independent validation unit, regular backtesting (PD, LGD), and sensitivity analysis.
*   **Governance**: Clear definition of lines of defense, model approval committees, and monitoring frameworks.

---

## 2. Definition of Default (Phase 3)

### 2.1 Alignment with CRR Article 178
The default definition aligns with Article 178 of the Capital Requirements Regulation (CRR) and EBA Guidelines (EBA/GL/2016/07).

### 2.2 Default Triggers
A default is considered to have occurred when either or both of the following have taken place:

1.  **Unlikeliness to Pay (UTP)**: The institution considers that the obligor is unlikely to pay its credit obligations in full without recourse to actions such as realizing security.
    *   **Indicators**:
        *   Distressed restructuring (forbearance resulting in a reduced financial obligation > 1% NPV loss).
        *   Bankruptcy or similar protection orders.
        *   Material credit-related sale at a loss (> 5%).
        *   Specific credit risk adjustment (> 20% provision).
        *   Cross-default/Contagion.

2.  **Days Past Due (DPD)**: The obligor is past due more than **90 days** on any material credit obligation to the institution.
    *   **Materiality Threshold** (RTS (EU) 2018/171):
        *   **Absolute**: > EUR 500 (Corporate).
        *   **Relative**: > 1% of total exposure.

### 2.3 Exit from Default (Cure)
An obligor can exit default status (cure) only when:
*   No default trigger continues to begin.
*   A probation period of at least **3 months** has elapsed (12 months for distressed restructuring).
*   The obligor has demonstrated a return to non-defaulted status and solvency.
---

## 3. Data Assessment & Preparation (Phase 2)

### 3.1 Data Inventory
*   **Historical Data**:
    *   Monthly obligor snapshots (20-year horizon in simulation).
    *   Payment history (DPD, amount past due).
    *   Financial statements (Revenue, EBITDA, Debt, Assets).
*   **Macroeconomic Data**:
    *   GDP Growth.
    *   Unemployment Rate.
    *   Interest Rates.
    *   Property Price Indices (for collateral).

### 3.2 Data Quality Framework
*   **Validation Rules**:
    *   No negative values for Exposure, Assets, Debt.
    *   PD must be between 0 and 1.
    *   Dates must be valid and sequential.
*   **Treatment**:
    *   Missing values: Imputation (filling with median/mean) or exclusion based on materiality (ECB guidelines).
    *   Outliers: Winsorization or capping/flooring at 1st/99th percentiles.

---

## 4. SICR Assessment Framework

### 4.1 Quantitative Triggers
*   **Relative Threshold**: Change in 12-month PD or Lifetime PD exceeds a specific percentage (e.g., 200% increase).
*   **Absolute Threshold**: PD exceeds a specific bps level (e.g., 50 bps increase).
*   **Backstop**: 30 Days Past Due.

### 4.2 Qualitative Triggers
*   Placement on "Watch List".
*   Forbearance status (performing).

---

## 5. ECL Methodology

### 5.1 Formula
$$ ECL = \sum (PD_{t} \times LGD_{t} \times EAD_{t} \times D_{t}) $$

*   **PD (Probability of Default)**: Point-in-Time (PIT) estimate, conditioned on macro scenarios.
*   **LGD (Loss Given Default)**: Estimate of loss severity, including downturn adjustments.
*   **EAD (Exposure at Default)**: Outstanding balance + CCF * Undrawn Commitment.
*   **D (Discount Factor)**: Effective Interest Rate (EIR).

### 5.2 Scenario Weighting
$$ ECL_{Final} = W_{Base} \times ECL_{Base} + W_{Optimist} \times ECL_{Optimist} + W_{Pessimist} \times ECL_{Pessimist} $$

*   Standard weights: 40% Base, 30% Optimistic, 30% Pessimistic (subject to governance review).

### 5.3 Lifetime ECL Extrapolation (Long-Dated Assets)
For assets with maturities exceeding the explicit forecast horizon (e.g., 30-year mortgages vs. 3-year macro forecasts), the model uses a **Mean Reversion** approach.

#### 1. Explicit Forecast Period (Reasonable & Supportable)
*   **Duration**: Years 1 to 3 (aligned with macro forecasts).
*   **Input**: Macro-linked PIT PD/LGD based on specific scenario forecasts.

#### 2. Reversion Period (Transition)
*   **Duration**: Years 4 to ~7 (Linear interpolation).
*   **Method**: Linearly interpolate input parameters (PD/LGD) from the Year 3 PIT value to the Long-Run Average (TTC) value.

#### 3. Long-Run Period (Equilibrium)
*   **Duration**: Year 7+ to Maturity.
*   **Input**: Long-Run Average (TTC) PDs and LGDs.
*   **Rationale**: Beyond the R&S period, the best estimate is the long-term cycle average.

#### 4. Discounting
$$ ECL_{Lifetime} = \sum_{t=1}^{T} \frac{ECL_t}{(1 + EIR)^t} $$
*   Losses in later years (e.g., year 25) are heavily discounted, reducing their PV impact.

### 5.4 Alternative Methodology: Transition Matrices (Markov Chain)
For portfolios with observable risk grades (e.g., Corporate Ratings 1-10 or Retail Delinquency Buckets), the **Markov Chain** approach is often preferred.

#### 1. The Transition Matrix ($M$)
A square matrix where $p_{ij}$ represents the probability of moving from State $i$ to State $j$ in one period (e.g., 1 year).
*   **Absorbing State**: "Default" is an absorbing state ($p_{DD} = 1$).

#### 2. Multi-Period (Time) Derivation
To derive the Cumulative PD for year $T$:
$$ M(0, T) = \prod_{t=1}^{T} M_{t} $$
*   If the matrix is constant (Homogeneous Markov Chain): $M(0, T) = M^T$.
*   The Lifetime PD for an obligor starting in Grade $i$ is the entry $(i, Default)$ in the matrix $M(0, T)$.

#### 3. Macro-Economic Conditioning (PIT Adjustment)
To comply with IFRS 9, the matrix $M$ must change every period $t$ based on economic conditions ($Z_t$).
*   **Method**: Shift the generator matrix $Q$ or adjust the boundaries of the Latent Variable in a Z-factor model applied to the migration thresholds.
*   **Result**: In a recession, the probability of downgrading ($p_{i \to i+1}$) increases, and upgrading ($p_{i \to i-1}$) decreases.
