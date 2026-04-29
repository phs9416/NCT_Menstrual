import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.io import loadmat
from nctpy.energies import integrate_u, get_control_inputs
from nctpy.utils import matrix_normalization, normalize_state

# ==========================================
# 1. Configuration
# ==========================================
DATA_DIR = '/home/phs9416/data'
CONNECTOME_BASE_DIR = "/home/phs9416/data/connectome_phase"

SUBJECTS = ["01", "02", "06", "07", "08", "09", "10", "11", "12", "13",
            "16", "19", "20", "23", "24", "25", "27", "28", "30", "32", "34", "35"]

N_DAYS = 30
N_NODES = 100

PHASE_DEFS = {
    "Follicular": list(range(11, 22)),
    "Ovulatory": list(range(22, 25)),
    "Luteal": list(range(1, 11)) + list(range(25, 31))
}
PHASE_SES_MAP = {"Follicular": "ses-01", "Ovulatory": "ses-02", "Luteal": "ses-03"}
PHASE_COLORS = {"Follicular": "lightblue", "Ovulatory": "lightpink", "Luteal": "khaki"}

# ==========================================
# 2. Helper Functions 
# ==========================================
def get_phase_for_day(day):
    for phase, days in PHASE_DEFS.items():
        if day in days: return phase
    return None

def compute_control_set(phase_name, days, thickness_data):
    mean_thickness = np.mean(thickness_data[:, [d - 1 for d in days]], axis=1)
    norm_sum = np.sum(mean_thickness)
    if norm_sum == 0: raise ValueError(f"Zero sum in thickness for {phase_name}")
    return np.diag((mean_thickness / norm_sum) * 100)

def calc_control_energy(A_norm, B, x0, xf):
    _, u, _ = get_control_inputs(
        A_norm=A_norm, T=1, B=B, x0=x0, xf=xf,
        system="continuous", rho=1, S=np.eye(N_NODES)
    )
    return np.sum(integrate_u(u))

def compute_ci(data):
    mean = np.nanmean(data, axis=0)
    lower = np.nanpercentile(data, 2.5, axis=0)
    upper = np.nanpercentile(data, 97.5, axis=0)
    return mean, lower, upper

# ==========================================
# 3. Data Loading & Preprocessing
# ==========================================

# (A) Brain states
mat_data = loadmat(os.path.join(DATA_DIR, 'SR_baseline_Schaefer100_Yeo17_Melbourn_S1.mat'))['SR'][0, 0]
brain_states_30 = mat_data['gradient_S_R_node'][:N_DAYS, :N_NODES] 

# (B) Cortical thickness & Control Sets
thickness_data = pd.read_csv(os.path.join(DATA_DIR, 'ThickAvg.schaefer100-yeo17.csv'), header=None).to_numpy()
control_set_dict = {
    phase: compute_control_set(phase, days, thickness_data) 
    for phase, days in PHASE_DEFS.items()
}
B_homog = np.eye(N_NODES)

# (C) Pre-load Connectomes 
sub_adj = {sub: {} for sub in SUBJECTS}
for sub in SUBJECTS:
    for phase, ses in PHASE_SES_MAP.items():
        path = os.path.join(CONNECTOME_BASE_DIR, ses, f"sub-{sub}.csv")
        if os.path.exists(path):
            sub_adj[sub][phase] = pd.read_csv(path, header=None).to_numpy()

# (D) Pill Baseline Data
energy_df = pd.read_csv(os.path.join(DATA_DIR, "all_subject_control_energy_matrix_1to60.csv"), index_col="Subject")
pill_cols = [f"Day_{i}" for i in list(range(31, 44)) + list(range(51, 60))]
pill_vals = energy_df[pill_cols].values.flatten()
pill_vals = pill_vals[~np.isnan(pill_vals)]
pill_mean = np.mean(pill_vals)
pill_std = np.std(pill_vals, ddof=1)

# ==========================================
# 4. Core Processing Pipeline
# ==========================================
n_trans = N_DAYS - 1
time_trans = np.arange(2, N_DAYS + 1)

eng_A_homog, eng_A_hetero = np.zeros((len(SUBJECTS), n_trans)), np.zeros((len(SUBJECTS), n_trans))
eng_C_homog, eng_C_hetero = np.zeros((len(SUBJECTS), n_trans)), np.zeros((len(SUBJECTS), n_trans))

for s_idx, sub in enumerate(SUBJECTS):
    if sub_adj[sub]:
        A_avg_C = np.mean(list(sub_adj[sub].values()), axis=0)
        A_norm_C = matrix_normalization(A=A_avg_C, system="continuous", c=1)
    else:
        A_norm_C = None

    for d in range(1, N_DAYS):
        phase = get_phase_for_day(d + 1)
        if phase is None: continue
        
        x0, xf = normalize_state(brain_states_30[d-1, :]), normalize_state(brain_states_30[d, :])
        B_hetero = control_set_dict.get(phase, B_homog)

        # Group A (Phase-specific Connectome)
        if phase in sub_adj[sub]:
            A_norm_A = matrix_normalization(A=sub_adj[sub][phase], system="continuous", c=1)
            eng_A_homog[s_idx, d-1] = calc_control_energy(A_norm_A, B_homog, x0, xf)
            eng_A_hetero[s_idx, d-1] = calc_control_energy(A_norm_A, B_hetero, x0, xf)
        else:
            eng_A_homog[s_idx, d-1], eng_A_hetero[s_idx, d-1] = np.nan, np.nan

        # Group C (Subject-averaged Connectome)
        if A_norm_C is not None:
            eng_C_homog[s_idx, d-1] = calc_control_energy(A_norm_C, B_homog, x0, xf)
            eng_C_hetero[s_idx, d-1] = calc_control_energy(A_norm_C, B_hetero, x0, xf)
        else:
            eng_C_homog[s_idx, d-1], eng_C_hetero[s_idx, d-1] = np.nan, np.nan

# Group D (Phase-averaged Connectome across all subjects)
eng_D_homog, eng_D_hetero = [], []
for d in range(1, N_DAYS):
    phase = get_phase_for_day(d + 1)
    if phase and phase in PHASE_SES_MAP:
        phase_adjs = [sub_adj[s][phase] for s in SUBJECTS if phase in sub_adj[s]]
        if phase_adjs:
            A_norm_D = matrix_normalization(A=np.mean(phase_adjs, axis=0), system="continuous", c=1)
            x0, xf = normalize_state(brain_states_30[d-1, :]), normalize_state(brain_states_30[d, :])
            eng_D_homog.append(calc_control_energy(A_norm_D, B_homog, x0, xf))
            eng_D_hetero.append(calc_control_energy(A_norm_D, control_set_dict[phase], x0, xf))
            continue
    eng_D_homog.append(np.nan)
    eng_D_hetero.append(np.nan)

mA_ho, lA_ho, uA_ho = compute_ci(eng_A_homog)
mA_he, lA_he, uA_he = compute_ci(eng_A_hetero)
mC_ho, lC_ho, uC_ho = compute_ci(eng_C_homog)
mC_he, lC_he, uC_he = compute_ci(eng_C_hetero)

# ==========================================
# 5. Visualization
# ==========================================
fig, ax1 = plt.subplots(figsize=(12, 7), facecolor='white')

# (1) Phase & Pill Backgrounds
for phase, days in PHASE_DEFS.items():
    valid_days = [d for d in days if 2 <= d <= 30]
    if valid_days:
        ax1.axvspan(min(valid_days), max(valid_days), color=PHASE_COLORS[phase], alpha=0.3, label=f"{phase} Phase" if f"{phase} Phase" not in ax1.get_legend_handles_labels()[1] else "")

ax1.fill_between(time_trans, pill_mean - 1.96*pill_std, pill_mean + 1.96*pill_std, color='gray', alpha=0.18, label="Pill Mean ± 1.96 SD")
ax1.axhline(pill_mean, color='black', linestyle='--', linewidth=1.2, label=f"Pill Mean = {pill_mean:.0f}")

# (2) Data Plotting Helper
def plot_series(ax, x, y, label, color, marker, ls, ci=None):
    ax.plot(x, y, color=color, marker=marker, linestyle=ls, linewidth=2, label=label)
    if ci: ax.fill_between(x, ci[0], ci[1], color=color, alpha=0.2)

plot_series(ax1, time_trans, mA_ho, "Group A Uniform", 'green', 'o', '-', (lA_ho, uA_ho))
plot_series(ax1, time_trans, mA_he, "Group A Cortical", 'orange', 's', '--', (lA_he, uA_he))
plot_series(ax1, time_trans, mC_ho, "Group C Uniform", 'gray', '^', '-', (lC_ho, uC_ho))
plot_series(ax1, time_trans, mC_he, "Group C Cortical", 'blue', 'v', '--', (lC_he, uC_he))
plot_series(ax1, time_trans, eng_D_homog, "Group D Uniform", 'purple', 'D', '-')
plot_series(ax1, time_trans, eng_D_hetero, "Group D Cortical", 'red', 'P', '--')

# (3) Formatting
ax1.set_xlim(2, N_DAYS)
ax1.set_ylim(500, 3000)
ax1.set_xlabel("Day", fontsize=12)
ax1.set_ylabel("Control Energy", fontsize=12)
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
ax1.grid(True, alpha=0.3)

# Hormone Data
try:
    df_h = pd.read_csv(os.path.join(DATA_DIR, "hormones_norm.csv"))
    df_h = df_h[(df_h["Day"] >= 2) & (df_h["Day"] <= N_DAYS)]
    ax2 = ax1.twinx()
    for col in ["Estradiol", "Progesterone", "LH", "FSH"]:
        if col in df_h.columns:
            norm_vals = (df_h[col] - df_h[col].min()) / (df_h[col].max() - df_h[col].min())
            ax2.plot(df_h["Day"], norm_vals, linewidth=1.8, alpha=0.95, label=col)
    ax2.set_ylabel("Normalized Hormones (0–1)")
    ax2.set_ylim(-0.05, 3.05)
except FileNotFoundError:
    print("No hormone data")

plt.tight_layout()
plt.savefig("Control_Energy_Hormones_2.jpg", dpi=300)
plt.show()