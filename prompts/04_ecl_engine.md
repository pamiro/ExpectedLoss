
/ifrs9-model-development.md @setup.md
Create ecl_engine.py.
- Implement the 3-Stage Impairment Model (Stage 1: 12m, Stage 2/3: Lifetime).
- Calculate ECL = Sum(PD_t * LGD_t * EAD_t * DiscountFactor_t).
- Ensure "Unbiased" estimate by probability-weighting the 3 macro scenarios (40/30/30).
Create example on how to use the ecl_engine.py with data produced by data_model.py.
