import os
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.spatial import distance
from scipy.io import loadmat
from sklearn.cluster import KMeans
from tqdm import tqdm
from nilearn import datasets, plotting

# import nctpy functions
from nctpy.energies import integrate_u, get_control_inputs
from nctpy.pipelines import ComputeControlEnergy, ComputeOptimizedControlEnergy
from nctpy.metrics import ave_control
from nctpy.utils import matrix_normalization, convert_states_str2int, normalize_state, normalize_weights, get_null_p, get_fdr_p
from nctpy.plotting import roi_to_vtx, null_plot, surface_plot, add_module_lines
from null_models.geomsurr import geomsurr

############# Group A Control Energy ######################

CONNECTOME_BASE_DIR = '/home/phs9416/data/connectome_schaefer100_symmetric/connectome_schaefer100_symmetric'
MAT_FILE_PATH = '/home/phs9416/data/SR_baseline_Schaefer100_Yeo17_Melbourn_S1.mat'
DATA_DIR = '/home/phs9416/data/'

subject_list = ["01", "02", "06", "07", "08", "09", "10", "11", "12", "13",
                "16", "19", "20", "23", "24", "25", "27", "28", "30", "32", "34", "35"]

phase_ses_map = {
    "Follicular": "ses-01",  # 11~21 days
    "Ovulatory": "ses-02",    # 22~24 days
    "Luteal": "ses-03"        # 1~10, 25~30 days
}

define_phases = {
    "Follicular": list(range(11, 22)),             
    "Ovulatory": list(range(22, 25)),               
    "Luteal": list(range(1, 11)) + list(range(25, 31)) 
}

mat_file = loadmat(MAT_FILE_PATH)
mat_data = mat_file['SR'][0, 0]

gradient_S_R_node = mat_data['gradient_S_R_node']
gradient_S_R_node_100 = gradient_S_R_node[:, 0:100]
brain_states_30 = gradient_S_R_node_100[:30, :]
n_days = brain_states_30.shape[0]  # 30 days
n_nodes = brain_states_30.shape[1] # 100 nodes

subject_energy_timeseries = {}   # subject_energy_timeseries[subject] = list of (day, total_energy)
subject_phase_avg = {}           # subject_phase_avg[subject] = {phase: average_energy, ...}

for sub in subject_list:
    print(f"Processing subject {sub} ...")
    time_series = [] 
    phase_energy = {phase: [] for phase in define_phases}
    
    # time step: day 1 ~ day 29 (each time step: d and d+1, d = 1-indexed)
    for d in range(1, n_days):  # d = 1,2,...,29
        current_phase = None
        for phase, days in define_phases.items():
            if d in days:
                current_phase = phase
                break
        if current_phase is None:
            continue
        
        ses = phase_ses_map[current_phase]
        adj_dir = os.path.join(CONNECTOME_BASE_DIR, ses)
        adj_file = os.path.join(adj_dir, f"sub-{sub}.csv")
        if not os.path.exists(adj_file):
            print(f"No file: {adj_file}")
            continue
        
        adjacency = pd.read_csv(adj_file, header=None).to_numpy()
        print(np.any(np.diag(adjacency) > 0))

        density = np.count_nonzero(np.triu(adjacency, k=0)) / (n_nodes*(n_nodes-1) / 2)
        print(density)

        # adjacency normalization (time system: continuous, c=1)
        A_norm = matrix_normalization(A=adjacency, system="continuous", c=1)

        initial_state = normalize_state(brain_states_30[d-1, :])
        target_state  = normalize_state(brain_states_30[d, :])

        # Control set: identity matrix
        control_set = np.eye(n_nodes)
        trajectory_constraints = np.eye(n_nodes)
        time_horizon = 1
        rho = 1
        system = "continuous"
    
        # control input calculation
        state_trajectory, control_signals, numerical_error = get_control_inputs(
            A_norm=A_norm,
            T=time_horizon,
            B=control_set,
            x0=initial_state,
            xf=target_state,
            system=system,
            rho=rho,
            S=trajectory_constraints
        )

        # control energy calculation (integrate_u)
        node_energy = integrate_u(control_signals)
        total_energy = np.sum(node_energy)

        time_series.append((d, total_energy))
        phase_energy[current_phase].append(total_energy)

    subject_energy_timeseries[sub] = time_series
    phase_avg = {}
    for phase, energies in phase_energy.items():
        if len(energies) > 0:
            phase_avg[phase] = np.mean(energies)
        else:
            phase_avg[phase] = np.nan
    subject_phase_avg[sub] = phase_avg

energy_dict = {}
for sub, ts in subject_energy_timeseries.items():
    ts_sorted = sorted(ts, key=lambda x: x[0])
    energy_values = [energy for (day, energy) in ts_sorted]
    energy_dict[sub] = energy_values

day_columns = [f"Day_{d}" for d in range(1, len(energy_values)+1)]
energy_df = pd.DataFrame.from_dict(energy_dict, orient='index', columns=day_columns)
energy_df.index.name = "Subject"

output_csv_path = os.path.join(DATA_DIR, "all_subject_control_energy_matrix.csv")
energy_df.to_csv(output_csv_path)
print(f"Control energy matrix saved to {output_csv_path}")

############# Group B Control Energy ######################

def get_phase_for_day(day, phase_definitions):
    for phase, days in phase_definitions.items():
        if day in days:
            return phase
    return None

MAT_FILE = '/home/phs9416/data/SR_baseline_Schaefer100_Yeo17_Melbourn_S1.mat'
mat_file = loadmat(MAT_FILE)
mat_data = mat_file['SR'][0, 0]
gradient_S_R_node = mat_data['gradient_S_R_node'] 
brain_states_full = gradient_S_R_node[:, 0:100]  
brain_states_30 = brain_states_full[:30, :]     
n_days = brain_states_30.shape[0]  # 30 days
n_nodes = brain_states_30.shape[1] # 100

fixed_adj_file = os.path.join('data', 'sc_train_s100.csv')
adjacency_fixed = pd.read_csv(fixed_adj_file, header=None).to_numpy()
print("Fixed connectome self-connections:", np.any(np.diag(adjacency_fixed) > 0))
A_norm_fixed = matrix_normalization(A=adjacency_fixed, system="continuous", c=1)

control_set_homog = np.eye(n_nodes)

control_set_dict = {}

energy_fixed_homog = []
time_points = np.arange(2, n_days+1)  # target day index (2~30)

for i in range(1, n_days):
    x0 = normalize_state(brain_states_30[i-1, :])
    xf = normalize_state(brain_states_30[i, :])
    
    phase = get_phase_for_day(i+1, define_phases)
    if phase is None:
        phase = "None"
    
    _, u_homog, _ = get_control_inputs(
        A_norm=A_norm_fixed,
        T=1,
        B=control_set_homog,
        x0=x0,
        xf=xf,
        system="continuous",
        rho=1,
        S=np.eye(n_nodes)
    )
    eng_homog = np.sum(integrate_u(u_homog))
    energy_fixed_homog.append(eng_homog)

energy_fixed_homog.to_csv('/home/phs9416/data/ControlEnergy.csv', index=False)
############# Group C & D Control Energy ######################

CONNECTOME_BASE_DIR = '/home/phs9416/data/connectome_phase'
DATA_DIR = '/home/phs9416/data/'
MAT_FILE_PATH = '/home/phs9416/data/SR_baseline_Schaefer100_Yeo17_Melbourn_S1.mat'

mat_file = loadmat(MAT_FILE_PATH)
mat_data = mat_file['SR'][0, 0]

gradient_S_R_node = mat_data['gradient_S_R_node']  
gradient_S_R_node_100 = gradient_S_R_node[:, :100]  
brain_states_30 = gradient_S_R_node_100[:30, :]   

n_days = brain_states_30.shape[0]   # 30
n_nodes = brain_states_30.shape[1]  # 100

### Group C connectome
group3_connectomes = {}
for sub in subject_list:
    connectomes = []
    for phase, ses in phase_ses_map.items():
        file_path = os.path.join(CONNECTOME_BASE_DIR, ses, f"sub-{sub}.csv")
        if os.path.exists(file_path):
            mat = pd.read_csv(file_path, header=None).values
            connectomes.append(mat)
    if connectomes:
        avg_connectome = np.mean(connectomes, axis=0)
        group3_connectomes[sub] = avg_connectome
        out_path = os.path.join(DATA_DIR, f"avg_connectome/group3_subject_avg_connectome_sub-{sub}.csv")
        pd.DataFrame(avg_connectome).to_csv(out_path, index=False, header=False)

### Group D connectome
group4_connectomes = {}
for phase, ses in phase_ses_map.items():
    connectomes = []
    for sub in subject_list:
        file_path = os.path.join(CONNECTOME_BASE_DIR, ses, f"sub-{sub}.csv")
        if os.path.exists(file_path):
            mat = pd.read_csv(file_path, header=None).values
            connectomes.append(mat)
    if connectomes:
        avg_connectome = np.mean(connectomes, axis=0)
        group4_connectomes[phase] = avg_connectome
        out_path = os.path.join(DATA_DIR, f"avg_connectome/group4_phase_avg_connectome_{phase}.csv")
        pd.DataFrame(avg_connectome).to_csv(out_path, index=False, header=False)

### Group C control energy
        
group3_energy = {}

for sub in subject_list:
    print(f"Computing Group 3 control energy for Subject {sub}...")
    adj_path = os.path.join(DATA_DIR, f"avg_connectome/group3_subject_avg_connectome_sub-{sub}.csv")
    if not os.path.exists(adj_path):
        print(f"Missing file: {adj_path}")
        continue
    A = pd.read_csv(adj_path, header=None).values
    A_norm = matrix_normalization(A, system="continuous", c=1)

    # control setting
    B = np.eye(n_nodes)  # full control
    S = np.eye(n_nodes)  # trajectory constraints
    T = 1
    rho = 1
    system = "continuous"

    # time series: 29 transitions (Day 1→2, 2→3, ..., 29→30)
    energies = []
    for d in range(1, n_days):  # d = 1 to 29
        x0 = normalize_state(brain_states_30[d-1])
        xf = normalize_state(brain_states_30[d])

        _, u, _ = get_control_inputs(A_norm, T, B, x0, xf, system, rho, S)
        e = np.sum(integrate_u(u))
        energies.append(e)

    group3_energy[sub] = energies

df_group3 = pd.DataFrame(group3_energy).T
df_group3.columns = [f"Day_{d}" for d in range(1, 30)]
df_group3.index.name = "Subject"

group3_out_path = os.path.join(DATA_DIR, "avg_connectome/all_subject_control_energy_matrix_group3.csv")
df_group3.to_csv(group3_out_path)
print(f"[✔] Group 3 energy matrix saved to: {group3_out_path}")

### Group D control energy 

day_phase_map = {}
for phase, days in define_phases.items():
    for d in days:
        day_phase_map[d] = phase

group4_energy = []

for d in range(1, n_days):  # day 1 ~ 29
    current_phase = day_phase_map[d]
    conn_path = os.path.join(DATA_DIR, f"avg_connectome/group4_phase_avg_connectome_{current_phase}.csv")
    A = pd.read_csv(conn_path, header=None).to_numpy()
    A_norm = matrix_normalization(A, system="continuous", c=1)
    
    x0 = normalize_state(brain_states_30[d - 1, :])
    xf = normalize_state(brain_states_30[d, :])
    B = np.eye(n_nodes)
    T = 1
    rho = 1
    S = np.eye(n_nodes)

    state_traj, control_signals, err = get_control_inputs(
        A_norm, T, B, x0, xf, "continuous", rho, S
    )
    
    energy = np.sum(integrate_u(control_signals))
    group4_energy.append(energy)

group4_df = pd.DataFrame([group4_energy], index=["Group4"], columns=[f"Day_{d}" for d in range(1, 30)])
output_path = os.path.join(DATA_DIR, "avg_connectome/all_subject_control_energy_matrix_group4.csv")
group4_df.to_csv(output_path)
print(f"✅ Group 4 energy matrix saved to: {output_path}")

