from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, ArrayType
import math

# Using lists for Matrix operations since Numpy is forbidden
# Matrix = List[List[float]]

class TransitionMatrixModel:
    """
    Implements Markov Chain estimation and conditioning for Credit Risk.
    """
    
    def __init__(self, rating_grades: list):
        """
        :param rating_grades: List of rating labels, e.g., ["AAA", "AA", ..., "D"]
                              The last state is assumed to be Default (Absorbing).
        """
        self.rating_grades = rating_grades
        self.n_states = len(rating_grades)
        self.default_state_index = self.n_states - 1
        
    def estimate_transition_matrix(self, transitions_df: DataFrame) -> list:
        """
        Estimates the empirical transition matrix from a DataFrame of transitions.
        Input DF must have columns: 'rating_start', 'rating_end', 'count' (or just rows).
        """
        # 1. Aggregation: Count (Start -> End)
        counts_df = transitions_df.groupBy("rating_start", "rating_end").count()
        rows = counts_df.collect()
        
        # 2. Build Count Matrix (Native Python)
        count_matrix = [[0.0 for _ in range(self.n_states)] for _ in range(self.n_states)]
        
        # Map labels to indices
        grade_map = {g: i for i, g in enumerate(self.rating_grades)}
        
        for row in rows:
            start_g = row['rating_start']
            end_g = row['rating_end']
            count = row['count']
            
            if start_g in grade_map and end_g in grade_map:
                i = grade_map[start_g]
                j = grade_map[end_g]
                count_matrix[i][j] = float(count)
                
        # 3. Normalize to Probabilities
        prob_matrix = []
        for i in range(self.n_states):
            row = count_matrix[i]
            total = sum(row)
            if total > 0:
                prob_row = [x / total for x in row]
            else:
                # If no observations, if Default state, stay in Default. Else Identity?
                prob_row = [0.0] * self.n_states
                if i == self.default_state_index:
                    prob_row[i] = 1.0 # Absorbing
                else:
                    prob_row[i] = 1.0 # Stay put (or handle missing data strategy)
            
            prob_matrix.append(prob_row)
            
        return prob_matrix

    def _inverse_normal_cdf(self, p):
        """Approximate Inverse Normal CDF (Acklam’s logic reused or simulated)"""
        # Simplified approximation for python-side logic (not UDF)
        # Using a simpler approximation for performance/conciseness in this class
        # (Winitzki approximation of erf -> inverse)
        if p >= 1.0 or p <= 0.0: return 0.0
        # ... actually, let's just implement a standard approximation to be safe
        
        # Coefficients for Acklam's (same as in PD PIT for consistency)
        a1, a2, a3, a4, a5, a6 = -3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00
        b1, b2, b3, b4, b5 = -5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01
        c1, c2, c3, c4, c5, c6 = -7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00
        d1, d2, d3, d4 = 7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00
        e1, e2, e3, e4, e5, e6 = 6.657904643501103e-03, 6.469399660036604e-01, 3.016036606598778e+02, 7.117885006608737e+03, 7.377729650203415e+04, 3.422420886858129e+05
        f1, f2, f3, f4 = 2.174396181152126e-02, 6.537337718563326e+01, 4.053259960754365e+03, 3.235543361849377e+05

        q = p - 0.5
        if abs(q) <= 0.425:
            r = 0.180625 - q * q
            return q * (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6) / (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1.0)
        else:
            r = p if q < 0 else 1.0 - p
            r = math.sqrt(-math.log(r))
            if r <= 5.0:
                r = r - 1.6
                val = (((((c1 * r + c2) * r + c3) * r + c4) * r + c5) * r + c6) / ((((d1 * r + d2) * r + d3) * r + d4) * r + 1.0)
            else:
                r = r - 5.0
                val = (((((e1 * r + e2) * r + e3) * r + e4) * r + e5) * r + e6) / ((((f1 * r + f2) * r + f3) * r + f4) * r + 1.0)
            return -val if q < 0 else val

    def _normal_cdf(self, x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def condition_matrix(self, ttc_matrix: list, z_factor: float, rho: float) -> list:
        """
        Conditions a TTC matrix on a Z-factor (Economy).
        Using the "Threshold Shifting" approach (Vasicek on Thresholds).
        """
        n = self.n_states
        pit_matrix = [[0.0] * n for _ in range(n)]
        
        # Pre-constants
        rho_sqrt = math.sqrt(rho)
        rho_compl_sqrt = math.sqrt(1 - rho)
        
        for i in range(n):
            if i == self.default_state_index:
                # Absorbing state (Default stays Default)
                pit_matrix[i][self.default_state_index] = 1.0
                continue
                
            # 1. Calculate Thresholds for row i
            # T_k is the threshold such that P(X < T_k) = Cumulative Prob up to state k
            cumulative_prob = 0.0
            thresholds = [] 
            
            # We iterate backwards from Best Rating to Worst Rating? 
            # Usually rating 0 is Best. P(0->0), P(0->1)...
            # Threshold T_0 corresponds to P(Migrat <= 0)
            
            for j in range(n - 1): # Last state is remaining prob
                cumulative_prob += ttc_matrix[i][j]
                # Clamp for numerical stability
                cp_safe = max(0.000001, min(0.999999, cumulative_prob))
                
                # Inverse Normal to get Threshold (TTC)
                thresh_ttc = self._inverse_normal_cdf(cp_safe)
                
                # Shift Threshold (PIT)
                # Conditional Probit Model: T_pit = (T_ttc - sqrt(rho)*Z) / sqrt(1-rho)
                thresh_pit_val = (thresh_ttc - rho_sqrt * z_factor) / rho_compl_sqrt
                thresholds.append(thresh_pit_val)
                
            # 2. Reconstruct Probabilities from PIT Thresholds
            prev_cdf = 0.0
            for j in range(n - 1):
                new_cdf = self._normal_cdf(thresholds[j])
                pit_matrix[i][j] = max(0.0, new_cdf - prev_cdf)
                prev_cdf = new_cdf
            
            # Last state (Default) gets the rest
            pit_matrix[i][n-1] = max(0.0, 1.0 - prev_cdf)
            
        return pit_matrix

    def multiply_matrices(self, A: list, B: list) -> list:
        """Standard Matrix Multiplication C = A x B"""
        n = self.n_states
        C = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if A[i][k] == 0: continue
                for j in range(n):
                    C[i][j] += A[i][k] * B[k][j]
        return C

    def calculate_cumulative_matrix(self, matrices: list) -> list:
        """Calculates product of a sequence of matrices M_1 * M_2 * ... * M_T"""
        if not matrices:
            # Return Identity
            return [[1.0 if i==j else 0.0 for j in range(self.n_states)] for i in range(self.n_states)]
            
        result = matrices[0]
        for m in matrices[1:]:
            result = self.multiply_matrices(result, m)
        return result

    def get_cumulative_pd_curve(self, start_rating_idx: int, cumulative_matrices: list) -> list:
        """Extracts the PD (Prob of Default state) for each time period from cumulative matrices"""
        pds = []
        for mat in cumulative_matrices:
            pd_val = mat[start_rating_idx][self.default_state_index]
            pds.append(pd_val)
        return pds

if __name__ == "__main__":
    from pyspark.sql import SparkSession
    import random
    
    try:
        spark = SparkSession.builder.appName("TransitionMatrixExamle").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        
        # 1. Define Ratings
        ratings = ["A", "B", "C", "Default"]
        tm_model = TransitionMatrixModel(ratings)
        
        # 2. Simulate Transition Data (Start -> End)
        data = []
        for _ in range(1000):
            r_start = random.choice(["A", "B", "C"]) # Don't start in default
            
            # Simple simulation logic
            roll = random.random()
            if r_start == "A":
                r_end = "A" if roll < 0.9 else ("B" if roll < 0.98 else "Default")
            elif r_start == "B":
                r_end = "B" if roll < 0.85 else ("A" if roll < 0.05 else ("C" if roll < 0.95 else "Default"))
            else: # C
                r_end = "C" if roll < 0.8 else "Default"
                
            data.append((r_start, r_end))
            
        df = spark.createDataFrame(data, ["rating_start", "rating_end"])
        
        print("Estimating TTC Matrix from data...")
        ttc_matrix = tm_model.estimate_transition_matrix(df)
        
        print("\nTTC Matrix:")
        for row in ttc_matrix:
            print([round(x, 4) for x in row])
            
        # 3. Apply Macro Conditioning
        z_recession = -2.0 # Bad economy
        print(f"\nConditioning on Recession (Z={z_recession})...")
        pit_matrix_rec = tm_model.condition_matrix(ttc_matrix, z_factor=z_recession, rho=0.15)
        
        print("Recession PIT Matrix:")
        for row in pit_matrix_rec:
            print([round(x, 4) for x in row])
            
        # 4. Multi-period Cumulative PD
        # Assume sequence of 3 years: Normal, Recession, Normal
        z_seq = [0.0, -2.0, 0.0]
        matrices = []
        cumulative_mats = []
        curr_cum = None
        
        print("\nCalculating Cumulative PDs over 3 years...")
        for z in z_seq:
            m = tm_model.condition_matrix(ttc_matrix, z_factor=z, rho=0.15)
            matrices.append(m)
            
            if curr_cum is None:
                curr_cum = m
            else:
                curr_cum = tm_model.multiply_matrices(curr_cum, m)
            cumulative_mats.append(curr_cum)
            
        # Extract PD for 'B' rated obligor
        b_idx = ratings.index("B")
        pds = tm_model.get_cumulative_pd_curve(b_idx, cumulative_mats)
        
        print(f"Cumulative PDs for 'B' rated obligor (Years 1-3): {[round(x,4) for x in pds]}")
        
    except Exception as e:
        print(f"Error: {e}")
