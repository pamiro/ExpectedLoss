# Model Validation Report: IFRS 9 Framework

**Date**: 2026-02-04
**Scope**: `src/` codebase (Data Model, PIT Model, Transition Matrix, ECL Engine)
**Standard**: IFRS 9 (IASB), ECB Guide to Internal Models, EBA Guidelines on ECL

---

## 1. Executive Summary

The reviewed framework implements a **hybrid Point-in-Time (PIT) / Through-the-Cycle (TTC)** approach compliant with IFRS 9 requirements. It successfully orchestrates the calculation of 12-month and Lifetime ECL using a forward-looking structure based on macroeconomic scenarios.

**Overall Rating**: **AMBER** (Conceptually Sound, Implementation Simplified)

### Key Strengths
*   **Methodological Soundness**: Adoption of the Vasicek Single Factor Model and Markov Chains for PIT conversion is industry standard for Retail/SME portfolios.
*   **IFRS 9 Compliance**: Correct implementation of the 3-Stage Impairment model and Discounting logic.
*   **Scenario Weighting**: Explicit "Unbiased Estimate" calculation using probability-weighted scenarios.

### Key Weaknesses (Gaps against ECB Guidelines)
*   **LGD/EAD Sophistication**: The current implementation uses simplified scalar adjustments for PIT LGD/EAD. ECB guidelines (TRIM) expect specific downturn modelling and structural recovery rate analysis.
*   **Data Quality**: While a schema exists, robust "Data Quality Indicators" (DQI) and stationarity tests required by ECB are not fully implemented in the pipeline.

---

## 2. Compliance Assessment (EBA Guidelines)

Assessment against *EBA/GL/2017/06 (Guidelines on credit institutions’ credit risk management practices and accounting for expected credit losses)*.

| EBA Section | Requirement | Compliance Status | Analysis |
| :--- | :--- | :--- | :--- |
| **4.2.1 (17)** | **Validation Process**: Institutions should have robust validation policies. | ⚠️ **Partial** | Validation logic is manual. No automated backtesting (Binomial tests, PSI) found in the `run_analysis.py` pipeline. |
| **4.2.3 (25)** | **PD Estimation**: Should reflect current economic conditions. | ✅ **Compliant** | `pd_pit_model.py` correctly links TTC PD to Macro Z-Factors to derive PIT PD. |
| **4.2.4 (30)** | **LGD Estimation**: Should capture forward-looking information. | ⚠️ **Partial** | LGD is adjusted by a scalar. Lack of component-based (Cure Rate, Recovery Costs) modelling limits precision. |
| **4.3.2 (45)** | **Scenario Selection**: Multiple scenarios required. | ✅ **Compliant** | `ecl_engine.py` explicitly handles Base, Optimistic, and Pessimistic scenarios with weighting. |
| **4.3.3 (50)** | **Discounting**: EIR should be used. | ✅ **Compliant** | `ecl_engine.py` correctly discounts flows using the facility-level Interest Rate. |
| **4.4.1 (55)** | **SICR Assessment**: Relative change in risk. | ⚠️ **Partial** | The analysis script uses a simplified bucket approach. A robust quantitative test (e.g., $\Delta PD > Threshold$) is implicit but not rigorously defined as a standalone module. |

---

## 3. Technical Code Analysis

### 3.1 `data_model.py`
*   **Observation**: Uses PySpark efficiently.
*   **Finding**: Generates plausible synthetic data, but the "Random" generation of Macro variables implies no correlation structure (e.g., GDP vs Unemployment), which is unrealistic for stress testing.
*   **Recommendation**: Implement Vector Autoregression (VAR) or Cholesky decomposition for correlated scenario generation.

### 3.2 `pd_pit_model.py` (Vasicek)
*   **Observation**: Implementation of Inverse Normal CDF using Acklam's approximation is excellent for establishing independence from SciPy.
*   **Finding**: The Correlation Factor $\rho$ is constant (0.15).
*   **Recommendation**: Allow $\rho$ to vary by Segment (e.g., Mortgages vs SME) as per Basel formulas.

### 3.3 `transition_matrix.py`
*   **Observation**: Matrix multiplication logic is correct.
*   **Finding**: The "Threshold Shifting" assumes a Gaussian Copula.
*   **Recommendation**: Verify that the starting "TTC Matrix" is truly Through-the-Cycle (i.e., average of many years) to avoid double-counting cycle effects.

---

## 4. Conclusion & Recommendations

The framework provides a **solid architectural foundation**. To move from "Prototype" to "Production" (Regulatory Approval status), the following actions are required:

1.  **Refine LGD Models**: Replace scalars with structural Workout LGD models.
2.  **Backtesting Module**: Create a new module `src/backtesting.py` to run Kolmogorov-Smirnov (KS) and Binomial tests on the outputs.
3.  **Governance**: formalized the definition of "Significant Increase in Credit Risk" (SICR) with specific quantitative thresholds in a config file.

---

## 5. Remediation Plan (Added by Validation Agent)
Based on the `ifrs9-cecl-validation` workflow, the following immediate actions are scheduled:
1.  **Correlation Engine**: Update `data_model.py` to use Cholesky decomposition for macro variable generation.
2.  **Granular Calibration**: Update `pd_pit_model.py` to differentiate Asset Correlation ($\rho$) by segment (Mortgage/SME/Retail).
3.  **Automated Testing**: Enhance `run_analysis.py` to include automatic Binomial Backtesting and PSI checks.
