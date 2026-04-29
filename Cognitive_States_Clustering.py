import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.anova import AnovaRM
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load the rmANOVA results
df_stats = pd.read_csv('rmANOVA_results.csv')

# Filter states with nominal significance in either Inbound or Outbound (p < 0.05)
sig_mask = (df_stats['p_Inbound'] < 0.05) | (df_stats['p_Outbound'] < 0.05)
sig_states = df_stats[sig_mask].copy()

# Calculate the differences (Follicular - Luteal)
# This represents the shift in energy during the Follicular phase relative to the Luteal phase
sig_states['Diff_Inbound'] = sig_states['Mean_Fol_In'] - sig_states['Mean_Lut_In']
sig_states['Diff_Outbound'] = sig_states['Mean_Fol_Out'] - sig_states['Mean_Lut_Out']

# Features for clustering
features = sig_states[['Diff_Inbound', 'Diff_Outbound']]

# Standardize features
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Apply KMeans Clustering
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
sig_states['Cluster'] = kmeans.fit_predict(features_scaled)

# Plotting the clusters
plt.figure(figsize=(10, 7))
colors = ['red', 'blue', 'green']
for cluster in range(3):
    cluster_data = sig_states[sig_states['Cluster'] == cluster]
    plt.scatter(cluster_data['Diff_Inbound'], cluster_data['Diff_Outbound'], 
                label=f'Cluster {cluster+1}', alpha=0.7, s=40)
    
    # Annotate top/representative points in each cluster
    for i, row in cluster_data.iterrows():
        name = row['State_Name']
        x, y = row['Diff_Inbound'], row['Diff_Outbound']
        
        # Default offsets
        dx, dy = 2, 2
        ha, va = 'left', 'bottom'

        right_aligned_states = ['autobiographical memory', 'response inhibition', 'focus', 'balance', 'imagery', 'selective attention']

        # Specific adjustments for overlapping labels requested by user
        if name in right_aligned_states:
            ha = 'right'
            dx = -2
        elif name == 'coordination': # often overlaps with response inhibition
            ha = 'right'
            va = 'top'
            dx, dy = -2, -2
        else:
            ha, va = 'left', 'bottom'

        plt.annotate(name, (x, y), 
                     xytext=(dx, dy), textcoords='offset points', 
                     fontsize=11, fontweight='medium',
                     ha=ha, va=va)
        '''
        plt.annotate(row['State_Name'], (row['Diff_Inbound'], row['Diff_Outbound']), 
                     fontsize=10, alpha=0.8)
        '''

plt.axhline(0, color='black', linestyle='--', linewidth=0.15)
plt.axvline(0, color='black', linestyle='--', linewidth=0.15)
plt.xlabel('Inbound Energy Delta (Follicular - Luteal)')
plt.ylabel('Outbound Energy Delta (Follicular - Luteal)')
plt.legend()
plt.grid(False)
plt.tight_layout()
plt.savefig('cognitive_state_clustering.jpg', dpi=300)

# Output cluster members
for i in range(3):
    print(f"\nCluster {i+1} States:")
    print(sig_states[sig_states['Cluster'] == i]['State_Name'].tolist())

# Save results for user
sig_states.to_csv('clustered_significant_states.csv', index=False)
