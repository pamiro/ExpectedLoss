---
description: IFRS9 Expected Credit Loss Model Development Agent - Following IFRS9 and ECB Guidelines
---

# IFRS9 Model Development Agent

This agent performs comprehensive IFRS9 Expected Credit Loss (ECL) model development in compliance with **IFRS9** (International Financial Reporting Standard 9) and **ECB** (European Central Bank) guidelines.

---

## 🎯 Agent Objectives

1. Develop robust ECL models for credit risk assessment
2. Ensure full compliance with IFRS9 requirements
3. Adhere to ECB supervisory expectations and guidelines
4. Produce comprehensive model documentation and validation reports

---

## 📋 Phase 1: Regulatory Framework Analysis

### 1.1 IFRS9 Requirements Assessment
- [ ] Review IFRS9 standard requirements for financial instruments classification
- [ ] Understand the three-stage impairment model (Stage 1, 2, 3)
- [ ] Document the Significant Increase in Credit Risk (SICR) criteria
- [ ] Map lifetime ECL vs 12-month ECL requirements
- [ ] Identify forward-looking information requirements

### 1.2 ECB Guidelines Review
- [ ] Review ECB Guide to internal models (IRB approach)
- [ ] Analyze ECB guidance on IFRS9 implementation
- [ ] Review ECB expectations on model validation
- [ ] Document ECB supervisory expectations on:
  - Definition of default
  - Probability of Default (PD) estimation
  - Loss Given Default (LGD) estimation
  - Exposure at Default (EAD) estimation
- [ ] Review ECB requirements on model governance

---

## 📊 Phase 2: Data Assessment & Preparation

### 2.1 Data Inventory
- [ ] Identify required data sources:
  - Historical default data (minimum 5-7 years recommended)
  - Recovery and cure data
  - Exposure data
  - Collateral information
  - Macroeconomic indicators
- [ ] Assess data quality and completeness
- [ ] Document data lineage and transformations

### 2.2 Data Quality Framework
- [ ] Implement data validation rules
- [ ] Handle missing values according to ECB guidelines
- [ ] Perform outlier detection and treatment
- [ ] Create data quality reports
- [ ] Establish data governance procedures

### 2.3 Segmentation Analysis
- [ ] Define portfolio segmentation criteria:
  - Product type
  - Customer type (retail, corporate, SME)
  - Collateral type
  - Geographic region
  - Risk characteristics
- [ ] Validate segment homogeneity
- [ ] Document segmentation rationale

---

## 🔢 Phase 3: PD Model Development

### 3.1 Default Definition
- [ ] Align with EBA/ECB definition of default (Article 178 CRR)
- [ ] Document default triggers:
  - 90 days past due threshold
  - Unlikeliness to pay indicators
  - Distressed restructuring
  - Bankruptcy/insolvency
- [ ] Validate default definition consistency

### 3.2 PD Estimation Methodology
- [ ] Select appropriate PD modeling approach:
  - Through-the-Cycle (TTC) PD
  - Point-in-Time (PIT) PD
  - Hybrid approaches
- [ ] Develop rating models:
  - Logistic regression
  - Survival analysis
  - Machine learning approaches (with explainability)
- [ ] Calibrate PD to long-run average
- [ ] Develop PD term structure (lifetime PD curves)

### 3.3 Forward-Looking Adjustments
- [ ] Identify relevant macroeconomic variables
- [ ] Develop macroeconomic scenarios:
  - Base scenario
  - Optimistic scenario
  - Pessimistic scenario
- [ ] Calculate probability-weighted average PD
- [ ] Document scenario selection methodology

### 3.4 SICR Assessment Framework
- [ ] Define quantitative SICR triggers:
  - Relative PD increase thresholds
  - Absolute PD thresholds
  - Days past due thresholds (30 days backstop)
- [ ] Define qualitative SICR indicators:
  - Watch list status
  - Forbearance measures
  - Industry stress indicators
- [ ] Implement stage allocation logic
- [ ] Develop cure rates for stage migration

---

## 💰 Phase 4: LGD Model Development

### 4.1 LGD Estimation Approach
- [ ] Select LGD methodology:
  - Workout LGD (observed recoveries)
  - Market LGD
  - Implied market LGD
- [ ] Define components:
  - Direct costs
  - Indirect costs
  - Discount rate selection
  - Time to recovery

### 4.2 Collateral Valuation
- [ ] Develop collateral haircut models
- [ ] Implement time-to-sale assumptions
- [ ] Model forced sale discounts
- [ ] Account for collateral revaluation under stress

### 4.3 Downturn LGD
- [ ] Identify economic downturn periods
- [ ] Estimate downturn LGD adjustments
- [ ] Apply ECB guidelines on downturn conditions

### 4.4 Forward-Looking LGD
- [ ] Link LGD to macroeconomic conditions
- [ ] Model recovery rate sensitivities
- [ ] Apply scenario-weighted LGD estimates

---

## 📈 Phase 5: EAD Model Development

### 5.1 EAD Estimation
- [ ] Model on-balance sheet exposures
- [ ] Estimate Credit Conversion Factors (CCF) for off-balance sheet items:
  - Committed unused limits
  - Guarantees
  - Letters of credit
- [ ] Model prepayment and amortization

### 5.2 Forward-Looking EAD
- [ ] Adjust EAD for drawdown behavior under stress
- [ ] Model facility maturity structures
- [ ] Apply behavioral maturity adjustments

---

## 🧮 Phase 6: ECL Calculation Engine

### 6.1 ECL Formula Implementation
```
ECL = Σ (PD × LGD × EAD × Discount Factor)
```
- [ ] Implement 12-month ECL calculation (Stage 1)
- [ ] Implement lifetime ECL calculation (Stage 2 & 3)
- [ ] Apply effective interest rate for discounting
- [ ] Handle multi-scenario probability weighting

### 6.2 Time Value of Money
- [ ] Select appropriate discount rate methodology
- [ ] Handle floating rate exposures
- [ ] Implement marginal ECL calculations

### 6.3 Collective vs Individual Assessment
- [ ] Define thresholds for individual assessment
- [ ] Implement collective assessment methodology
- [ ] Document assessment criteria

---

## ✅ Phase 7: Model Validation

### 7.1 Quantitative Validation
- [ ] Perform backtesting analysis:
  - PD backtesting (Binomial test, Traffic light approach)
  - LGD backtesting (Mean absolute deviation)
  - EAD backtesting
- [ ] Conduct benchmarking exercises
- [ ] Perform sensitivity analysis
- [ ] Calculate model performance metrics:
  - Accuracy Ratio / Gini coefficient
  - AUC-ROC
  - Population Stability Index (PSI)
  - Hosmer-Lemeshow test

### 7.2 Qualitative Validation
- [ ] Review methodology documentation
- [ ] Assess data quality and representativeness
- [ ] Review model assumptions
- [ ] Evaluate model use test
- [ ] Review model governance framework

### 7.3 Stress Testing
- [ ] Perform portfolio stress testing
- [ ] Assess model behavior under extreme conditions
- [ ] Validate scenario generation process

---

## 📝 Phase 8: Documentation & Governance

### 8.1 Model Documentation (ECB Requirements)
- [ ] Create comprehensive model documentation including:
  - Executive summary
  - Methodology description
  - Data requirements and sources
  - Model development process
  - Validation results
  - Implementation details
  - Known limitations
  - Model monitoring framework

### 8.2 Regulatory Reporting
- [ ] Prepare FINREP/COREP templates
- [ ] Document staging movements
- [ ] Prepare ECL movement reconciliation
- [ ] Create disclosure reports (IFRS7)

### 8.3 Model Risk Management
- [ ] Establish model inventory
- [ ] Define model risk appetite
- [ ] Implement model monitoring KPIs
- [ ] Define trigger events for model recalibration
- [ ] Establish annual review schedule

---

## 🔄 Phase 9: Implementation & Monitoring

### 9.1 Technical Implementation
- [ ] Develop calculation engine
- [ ] Integrate with core banking systems
- [ ] Implement audit trails
- [ ] Establish data feeds and automation

### 9.2 Ongoing Monitoring
- [ ] Define monitoring frequency
- [ ] Implement early warning indicators
- [ ] Track model performance metrics
- [ ] Monitor portfolio composition changes
- [ ] Review macroeconomic outlook updates

### 9.3 Model Recalibration Triggers
- [ ] Portfolio composition changes > threshold
- [ ] Significant backtesting failures
- [ ] Material methodology updates
- [ ] Regulatory requirement changes

---

## 📚 Key Regulatory References

### IFRS9 Standards
- IFRS 9 Financial Instruments (2014)
- IFRS 7 Financial Instruments: Disclosures
- ITG (IFRS Transition Resource Group) clarifications

### ECB Guidelines
- ECB Guide to internal models (IRB approach)
- ECB Guidance on leveraged transactions
- ECB supervisory expectations on IFRS9
- EBA Guidelines on credit risk management
- EBA Guidelines on PD estimation, LGD estimation, and treatment of defaulted exposures

### Additional References
- Basel Committee guidance on expected credit losses
- CRR/CRD IV requirements
- EBA ITS on supervisory reporting

---

## ⚠️ Key Compliance Checkpoints

> [!IMPORTANT]
> - Ensure alignment with EBA definition of default
> - Validate 12-month vs lifetime ECL stage allocation
> - Document forward-looking information methodology
> - Maintain complete audit trail for all model decisions
> - Establish independent model validation

> [!WARNING]
> Common pitfalls to avoid:
> - Insufficient historical data coverage
> - Inadequate SICR threshold calibration
> - Missing forward-looking adjustments
> - Incomplete documentation
> - Lack of model governance framework

---

## 🎯 Success Criteria

1. ✅ All ECL model components (PD, LGD, EAD) developed and validated
2. ✅ Full compliance with IFRS9 three-stage impairment requirements
3. ✅ ECB guideline compliance demonstrated
4. ✅ Comprehensive model documentation completed
5. ✅ Validation reports with satisfactory backtesting results
6. ✅ Model governance framework established
7. ✅ Ongoing monitoring procedures implemented