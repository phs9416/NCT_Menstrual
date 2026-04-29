import os
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.io import loadmat
from scipy.stats import pearsonr, norm

CONNECTOME_BASE_DIR = '/home/phs9416/data/connectome_phase'
DATA_DIR = '/home/phs9416/data/'
subject_list = ["01", "02", "06", "07", "08", "09", "10", "11", "12", "13",
                "16", "19", "20", "23", "24", "25", "27", "28", "30", "32", "34", "35"]

phase_ses_map = {
    "Follicular": "ses-01",
    "Ovulatory": "ses-02",
    "Luteal": "ses-03"
}

MAT_FILE_PATH = '/home/phs9416/data/SR_baseline_Schaefer100_Yeo17_Melbourn_S1.mat'

group1_path = os.path.join(DATA_DIR, "all_subject_control_energy_matrix.csv")
group3_path = os.path.join(DATA_DIR, "avg_connectome/all_subject_control_energy_matrix_group3.csv")
group4_path = os.path.join(DATA_DIR, "avg_connectome/all_subject_control_energy_matrix_group4.csv")

group1_df = pd.read_csv(group1_path, index_col=0)
group3_df = pd.read_csv(group3_path, index_col=0)
group4_df = pd.read_csv(group4_path, index_col=0)

combined_df = pd.concat([group1_df, group3_df, group4_df])
output_path = os.path.join(DATA_DIR, "combined_control_energy_matrix.csv")
combined_df.to_csv(output_path)
print(f"✅ All groups merged and saved to: {output_path}")

from scipy.stats import pearsonr
import itertools

combined_df = pd.read_csv("/home/phs9416data/combined_control_energy_matrix.csv", index_col=0)

group_A = combined_df.iloc[0:22].values          # Group A
group_C = combined_df.iloc[22:44].values         # Group C
group_D = combined_df.iloc[44:45].values         # Group D 
group_B = pd.read_csv("/home/phs9416/data/ControlEnergy.csv", header=None).head(29).values.reshape(1, -1)

group_dict = {
    "Group_A": group_A,
    "Group_B": group_B,
    "Group_C": group_C,
    "Group_D": group_D,
}

############### Comparison of group-level control energy correlations ########

# Fisher z-transform
fisher_z = lambda r: 0.5 * np.log((1 + r) / (1 - r))
fisher_z_inv = lambda z: (np.exp(2*z) - 1) / (np.exp(2*z) + 1)

def internal_correlations(group):
    corrs = []
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            r, _ = pearsonr(group[i], group[j])
            corrs.append(r)
    return np.array(corrs)

def external_correlations(subject, group):
    return np.array([pearsonr(subject, g)[0] for g in group])

def fisher_z_test(r1, r2, n1, n2):
    z1 = np.mean(fisher_z(r1))
    z2 = np.mean(fisher_z(r2))
    se = np.sqrt(1/(n1 - 3) + 1/(n2 - 3))
    z = (z1 - z2) / se
    p = 2 * (1 - norm.cdf(abs(z)))
    return z, p

internal_A = internal_correlations(group_A)
internal_C = internal_correlations(group_C)
external_BA = external_correlations(group_B.flatten(), group_A)
external_BC = external_correlations(group_B.flatten(), group_C)
external_DA = external_correlations(group_D.flatten(), group_A)
external_DC = external_correlations(group_D.flatten(), group_C)
external_BD = np.array([pearsonr(group_B.flatten(), group_D.flatten())[0]])

# Fisher z-test
results = []
comparisons = [
    (internal_A, external_BA, len(group_A), len(external_BA), "B vs A"),
    (internal_C, external_BC, len(group_C), len(external_BC), "B vs C"),
    (internal_A, external_DA, len(group_A), len(external_DA), "D vs A"),
    (internal_C, external_DC, len(group_C), len(external_DC), "D vs C"),
    (external_BA, external_BD, len(external_BA), 1, "B vs D"),
    (internal_A, internal_C, len(group_A), len(group_C), "A vs C")
]

for r1, r2, n1, n2, label in comparisons:
    if n2 < 2:
        z, p = np.nan, np.nan
    else:
        z, p = fisher_z_test(r1, r2, n1, n2)
    results.append({"Comparison": label, "Z-score": z, "p-value": p})

results_df = pd.DataFrame(results)

plt.figure(figsize=(10, 6))
sns.barplot(data=results_df, x="Comparison", y="p-value", color="skyblue")
plt.axhline(0.05, color='red', linestyle='--', label='p = 0.05')
for i, p in enumerate(results_df["p-value"]):
    if p < 0.05:
        plt.text(i, p + 0.01, "*", ha='center', va='bottom', fontsize=14, color='darkred')
plt.ylabel("p-value (Fisher z-test)")
plt.legend()
plt.tight_layout()
plt.show()
print(results_df)

#################### Distribution of within-group and inter-group correlations for control energy trajectories ########

def compute_internal_z(group):
    z_scores = []
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            r, _ = pearsonr(group[i], group[j])
            z_scores.append(fisher_z(r))
    return z_scores

def compute_external_z(subject, group):
    return np.mean([fisher_z(pearsonr(subject, g)[0]) for g in group])

def compute_pairwise_z(group1, group2):
    z_scores = []
    for x in group1:
        for y in group2:
            r, _ = pearsonr(x, y)
            z_scores.append(fisher_z(r))
    return np.mean(z_scores), z_scores

z_A = compute_internal_z(group_A)
z_C = compute_internal_z(group_C)
mean_z_BA = compute_external_z(group_B.flatten(), group_A)
mean_z_DA = compute_external_z(group_D.flatten(), group_A)
mean_z_CA, _ = compute_pairwise_z(group_C, group_A)
mean_z_BC = compute_external_z(group_B.flatten(), group_C)
mean_z_DC = compute_external_z(group_D.flatten(), group_C)

plt.figure(figsize=(12, 6))
plt.hist(z_A, bins=20, color='lightblue', alpha=0.6, label='Within Group A (z)')
plt.hist(z_C, bins=20, color='orange', alpha=0.6, label='Within Group C (z)')
plt.axvline(mean_z_BA, color='red', linestyle='--', label='Group B vs A')
plt.axvline(mean_z_DA, color='green', linestyle='--', label='Group D vs A')
plt.axvline(mean_z_CA, color='purple', linestyle='--', label='Group C vs A')
plt.axvline(mean_z_BC, color='blue', linestyle='--', label='Group B vs C')
plt.axvline(mean_z_DC, color='cyan', linestyle='--', label='Group D vs C')
plt.xlabel("Fisher's z-transformed Pearson r")
plt.ylabel("Frequency")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()