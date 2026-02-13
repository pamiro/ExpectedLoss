
/ifrs9-model-development.md @setup.md
Create pd_pit_model.py model part of the framework dedicated to fitting TTC PDs to PIT PDs.
Implement a Vasicek Single Factor model to convert Through-the-Cycle (TTC) PDs to Point-in-Time (PIT) PDs.
- Link the "Z-factor" to the macroeconomic variables defined in the arbitrary data model.
- Apply similar macro-conditioning to LGD (Downturn LGD) and EAD.
- Ensure Asset Correlation (rho) varies by Segment (Mortgage vs Retail vs SME) according to Basel formulas.
Create example on how to use the pd_pit_model.py with data produced by data_model.py.
