import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from nctpy.pipelines import ComputeControlEnergy, ComputeOptimizedControlEnergy
from nctpy.utils import normalize_state
from statsmodels.formula.api import ols
from statsmodels.stats.anova import AnovaRM

subject_list = ["01", "02", "06", "07", "08", "09", "10", "11", "12", "13",
                "16", "19", "20", "23", "24", "25", "27", "28", "30", "32", "34", "35"]
phase_ses_map = {
    "Follicular": "ses-01",
    "Ovulatory": "ses-02",
    "Luteal": "ses-03"
}

# Cortex thickness 
thickness_file_path = "/home/phs9416/data/ThickAvg.schaefer100-yeo17.csv"
cortex_thickness = pd.read_csv(thickness_file_path, header=None).to_numpy()

# Phase
define_phases = {
    "Follicular": list(range(11, 23)),
    "Ovulatory": list(range(23, 26)),
    "Luteal": list(range(1, 11)) + list(range(26, 31)),
}

def calculate_mean_thickness(cortex_thickness, days):
    return np.mean(cortex_thickness[:, days], axis=1)

# Control sets 
control_sets = {}
for phase, days in define_phases.items():
    mean_thickness = calculate_mean_thickness(cortex_thickness, [day - 1 for day in days])
    norm_sum = np.sum(mean_thickness)
    normalized_thickness = mean_thickness / norm_sum if norm_sum != 0 else mean_thickness
    scaled_control_values = normalized_thickness * 100 
    control_sets[phase] = np.diag(scaled_control_values)

# Brain state 
brain_states_file_path = "/home/phs9416/data/top123_S100.csv"
brain_states = pd.read_csv(brain_states_file_path, header=None).to_numpy()

is_zero_vector = np.all(brain_states == 0, axis=1)
brain_states = brain_states[~is_zero_vector]

# State normalization
normalized_states = np.array([normalize_state(state) for state in brain_states])
n_states = normalized_states.shape[0]

subject_energy_matrices = []  

for sub in subject_list:
    for phase, ses in phase_ses_map.items():
        print(f"Processing Sub-{sub}, Phase-{phase}...")

        # Adjacency matrix
        adjacency_file_path = f"/home/phs9416/data/connectome_schaefer100/{ses}/sub-{sub}.csv"
        raw = pd.read_csv(adjacency_file_path, header=None)
        raw = raw + raw.T - np.diag(np.diag(raw))
        adjacency = raw.to_numpy()
        n_nodes = adjacency.shape[0]

        # Control set
        control_set = control_sets[phase]

        # Control task 
        control_tasks = []
        for initial_idx in range(len(normalized_states)):
            for target_idx in range(len(normalized_states)):
                control_tasks.append({
                    "x0": normalized_states[initial_idx],
                    "xf": normalized_states[target_idx],
                    "B": control_set,
                    "S": np.eye(n_nodes),
                    "rho": 1
                })

        # Control energy 
        compute_control_energy = ComputeControlEnergy(A=adjacency, control_tasks=control_tasks, system="continuous", c=1, T=1)
        compute_control_energy.run()

        # Energy matrix 
        energy_matrix = np.reshape(compute_control_energy.E, (n_states, n_states))

        # Column sum (Inbound) & Row sum (Outbound) 
        inbound_energy = np.sum(energy_matrix, axis=0)  
        outbound_energy = np.sum(energy_matrix, axis=1)  

        for i in range(n_states):
            subject_energy_matrices.append({
                "Subject": sub,
                "Phase": phase,
                "State": i+1,
                "Inbound_Energy": inbound_energy[i],
                "Outbound_Energy": outbound_energy[i]
            })

energy_df = pd.DataFrame(subject_energy_matrices)

save_path = os.path.join("/home/phs9416/data", "energy_results_inandout.csv")
energy_df.to_csv(save_path, index=False)
