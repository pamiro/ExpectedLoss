# IFRS 9 Framework Improvements

Based on the analysis of the `src` folder against the `src/validation_report.md` and the `ifrs9-cecl-validation` workflow, the following improvements are required for the next iteration of the framework.

## 1. Data Generation (`data_model.py`)
**Current State**: Macro variables are generated using independent random processes (`F.rand()`), resulting in zero correlation between GDP, Unemployment, etc.
**Requirement**:
- Implement **Vector Autoregression (VAR)** or **Cholesky Decomposition** to ensure macro variables are correlated.
- Example: High Unemployment should correlate with Low GDP Growth.

## 2. PIT Model (`pd_pit_model.py`)
**Current State**: The Asset Correlation factor ($\rho$) is hardcoded to 0.15 for all segments.
**Requirement**:
- Implement **Basel A-IRB Correlation Formulas**.
- $\rho$ should vary by Segment:
    - **Mortgages**: Fixed or dependent on default rate.
    - **SME**: Dependent on Turnover.
    - **Revolving**: Different constant.

## 3. LGD & EAD Modelling
**Current State**: LGD and EAD are adjusted using simple scalar multipliers (e.g., `LGD * (1 - 0.05 * Z)`).
**Requirement**:
- Implement **Downturn LGD** logic more formally.
- If possible, separate Cure Rate and Severity components.

## 4. Validation & Backtesting (`run_analysis.py`)
**Current State**: No quantitative validation is performed during execution.
**Requirement**:
- Implement a **Backtesting Module** containing:
    - **Binomial Test**: To test PD calibration (Predicted vs Realized).
    - **PSI (Population Stability Index)**: To test distribution stability.
- These tests should be run automatically at the end of the pipeline.

## 5. Governance & SICR
**Current State**: Stage allocation is random/implicit.
**Requirement**:
- Define explicit **Quantitative SICR Thresholds** (e.g., if PD_Lifetime / PD_Origination > 2.5, move to Stage 2).

---

## Action Plan
The prompts in `prompts/` will be updated to explicitly request these features in the next code generation cycle.
