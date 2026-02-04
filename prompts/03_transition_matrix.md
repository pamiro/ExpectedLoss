
/ifrs9-model-development.md @setup.md
Create transition_matrix.py.
- Implement logic to estimate yearly Transition Matrices (Migration between Rating Grades).
- Ensure matrices are conditioned on the economic cycle (shift downgrade probs in recession).
- Implement multi-period multiplication M(0,T) to derive Cumulative PD curves.
Create example on how to use the transition_matrix.py with data produced by data_model.py.
