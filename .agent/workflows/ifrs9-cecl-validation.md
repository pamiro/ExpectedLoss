---
description: IFRS9/CECL Model Validation & Testing Agent - ECB/EBA Compliance Focused
---

# IFRS9 & CECL Model Validation Agent

This workflow defines the specialized validation process for Expected Credit Loss (ECL) models, ensuring strict compliance with **European Banking Regulations** (CRR, EBA, ECB) while covering **IFRS 9** and **CECL** (ASC 326) accounting standards.

---

## 🏛️ 1. Regulatory Framework & Standards

The validation activities must adhere to the following hierarchy of standards:

### Primary Regulations (EU)
*   **CRR (Regulation EU No 575/2013)**:
    *   *Article 174*: Estimation of risk parameters.
    *   *Article 185*: Validation of internal estimates.
*   **EBA Guidelines**:
    *   *EBA/GL/2017/16*: Guidelines on PD estimation, LGD estimation, and the treatment of defaulted exposures.
    *   *EBA/GL/2016/07*: Definition of Default.
*   **ECB Guide to Internal Models (TRIM)**:
    *   *Credit Risk Chapter*: Specific supervisory expectations for IFRS 9 ECL models.

### Accounting Standards
*   **IFRS 9**: Financial Instruments (IASB).
*   **ASC 326**: Financial Instruments - Credit Losses (CECL) [for dual-reporting entities].

---

## 📋 2. Validation Workflow

### Step 2.1: Regulatory Compliance Check (Gap Analysis)
- [ ] Verify **Definition of Default** alignment with EBA/GL/2016/07 (90 days, UTP tokens).
- [ ] Confirm **SICR** (Significant Increase in Credit Risk) triggers include:
    *   Quantitative (PD threshold).
    *   Qualitative (Watchlist).
    *   Backstop (30 DPD).
- [ ] Ensure **Pessimistic/Optimistic Scenarios** are distinct and probabilistically weighted.
- [ ] Validate **Discounting** uses Effective Interest Rate (EIR).

### Step 2.2: Data Integrity & Quality (EDQI)
- [ ] **Completeness**: Check for missing payment history or financial statements.
- [ ] **Accuracy**: Reconcile with Risk Data Mart (RDM) and General Ledger.
- [ ] **Representativeness**: Ensure defective data (COVID-19 moratoriums) is treated per ECB guidelines.

### Step 2.3: Quantitative Performance Testing

#### A. Discriminatory Power (Ranking)
*   **Metric**: AUC (ROC Area), Gini Coefficient.
*   **Thresholds**:
    *   Gini > 60% (Retail), Gini > 50% (Corporate).
*   **Test**: Compare Model Ranking vs Realized Defaults.

#### B. Calibration (Bucket Level)
*   **Metric**: Binomial Test, Traffic Light Approach (green/orange/red).
*   **Test**: Compare Potential Default Rates (PD) vs Realized Default Rates (DR) per rating grade.
    *   *ECB Requirement*: PD should not systematically underestimate DR.

#### C. Stability (PSI)
*   **Metric**: Population Stability Index (PSI).
*   **Threshold**: PSI < 0.10 (Stable).
*   **Check**: Compare current portfolio distribution vs training data distribution.

### Step 2.4: IFRS 9 Specific Testing
- [ ] **Stage Allocation Stability**: Analyze "flipper" accounts (accounts oscillating between Stage 1 and 2).
- [ ] **ECL Sensitivity**: Test impact of Macroeconomic Scenarios (e.g., GDP drop -2% vs -5%).
- [ ] **LGD Downturn**: Verify LGD params reflect economic downturn conditions (Stage 3).

---

## 🛠️ 3. Validation Report Structure (Template)

1.  **Executive Summary**: Verification Opinion (Approved/Restricted/Rejected).
2.  **Scope**: Models covered (Retail Mortgages, Corporate, SME).
3.  **Data Quality**: Summary of data limitations.
4.  **Methodology Review**: Conceptual soundness assessment.
5.  **Quantitative Results**:
    *   *Backtesting tables*.
    *   *Benchmarking against Challenger Models*.
6.  **Findings & Remediation**:
    *   Severe (Red): Must fix before implementation.
    *   Significant (Amber): Fix within 3-6 months.
    *   Minor (Green): Continuous improvement.

---

## ⚠️ Common Regulatory Findings (ECB TRIM)
> [!WARNING]
> *   **Lack of Margin of Conservatism (MoC)**: Models must include MoC for data deficiencies.
> *   **Over-reliance on expert judgment**: All qualitative overrides must be monitored.
> *   **Pro-cyclicality**: Point-in-Time (PIT) PDs must react to cycle changes, but avoid excessive volatility.
