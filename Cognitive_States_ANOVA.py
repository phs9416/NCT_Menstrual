import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.anova import AnovaRM
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

######## RM ANOVA #######################

# Load data
df = pd.read_csv('energy_results_with_state_names.csv')

states = df['State'].unique()
rm_results = []

for state in states:
    state_df = df[df['State'] == state]
    state_name = state_df['State_Name'].iloc[0]
    
    # rmANOVA for Inbound_Energy
    res_in = AnovaRM(data=state_df, depvar='Inbound_Energy', subject='Subject', within=['Phase']).fit()
    f_in = res_in.anova_table['F Value'][0]
    p_in = res_in.anova_table['Pr > F'][0]
    
    # rmANOVA for Outbound_Energy
    res_out = AnovaRM(data=state_df, depvar='Outbound_Energy', subject='Subject', within=['Phase']).fit()
    f_out = res_out.anova_table['F Value'][0]
    p_out = res_out.anova_table['Pr > F'][0]
    
    # Means for context
    mean_fol_in = state_df[state_df['Phase'] == 'Follicular']['Inbound_Energy'].mean()
    mean_lut_in = state_df[state_df['Phase'] == 'Luteal']['Inbound_Energy'].mean()
    mean_fol_out = state_df[state_df['Phase'] == 'Follicular']['Outbound_Energy'].mean()
    mean_lut_out = state_df[state_df['Phase'] == 'Luteal']['Outbound_Energy'].mean()
    
    rm_results.append({
        'State': state,
        'State_Name': state_name,
        'F_Inbound': f_in,
        'p_Inbound': p_in,
        'F_Outbound': f_out,
        'p_Outbound': p_out,
        'Mean_Fol_In': mean_fol_in,
        'Mean_Lut_In': mean_lut_in,
        'Mean_Fol_Out': mean_fol_out,
        'Mean_Lut_Out': mean_lut_out
    })

rm_stats_df = pd.DataFrame(rm_results)

# FDR correction
_, p_adj_in, _, _ = multipletests(rm_stats_df['p_Inbound'], method='fdr_bh')
_, p_adj_out, _, _ = multipletests(rm_stats_df['p_Outbound'], method='fdr_bh')
rm_stats_df['p_adj_Inbound'] = p_adj_in
rm_stats_df['p_adj_Outbound'] = p_adj_out

# Filter nominally significant ones for the report
sig_in = rm_stats_df[rm_stats_df['p_Inbound'] < 0.05].sort_values('p_Inbound')
sig_out = rm_stats_df[rm_stats_df['p_Outbound'] < 0.05].sort_values('p_Outbound')

print("Top Nominally Significant Inbound (rmANOVA):")
print(sig_in[['State_Name', 'F_Inbound', 'p_Inbound']].head(5))

print("\nTop Nominally Significant Outbound (rmANOVA):")
print(sig_out[['State_Name', 'F_Outbound', 'p_Outbound']].head(5))

# Save results
rm_stats_df.to_csv('rmANOVA_results.csv', index=False)


