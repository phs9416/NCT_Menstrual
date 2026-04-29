import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('/home/phs9416/data/ThickAvg.schaefer100-yeo17.csv', header=None)

df_long = df.reset_index().rename(columns={'index': 'Region'})
df_long = df_long.melt(id_vars='Region', var_name='Timepoint', value_name='Thickness')

df_long['Day'] = df_long['Timepoint'].astype(int) + 1

def get_phase(day):
    if 11 <= day <= 21:
        return 'Follicular'
    elif 22 <= day <= 24:
        return 'Ovulatory'
    elif (1 <= day <= 10) or (25 <= day <= 30):
        return 'Luteal'
    elif 31 <= day <= 45:
        return 'Oral Contraceptive'
    else:
        return 'Rest' 

# Natural Cycle vs OC
df_long['Phase'] = df_long['Day'].apply(get_phase)
df_long['Is_OC'] = df_long['Day'].apply(lambda x: 'OC Period' if 31 <= x <= 45 else ('Natural Cycle' if 1 <= x <= 30 else 'Rest'))

df_analysis = df_long[df_long['Phase'] != 'Rest'].copy()
df_period_compare = df_long[df_long['Is_OC'] != 'Rest'].copy()

model_phase = smf.mixedlm("Thickness ~ C(Phase, Treatment(reference='Oral Contraceptive'))", 
                          df_analysis, 
                          groups=df_analysis["Region"])
result_phase = model_phase.fit()
print(result_phase.summary())

model_period = smf.mixedlm("Thickness ~ C(Is_OC, Treatment(reference='Natural Cycle'))", 
                           df_period_compare, 
                           groups=df_period_compare["Region"])
result_period = model_period.fit()

print(result_period.summary())


plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
phase_order = ['Follicular', 'Ovulatory', 'Luteal', 'Oral Contraceptive']
sns.boxplot(x='Phase', y='Thickness', data=df_analysis, order=phase_order, palette='Set3')
plt.title('Cortical Thickness by Phase')
plt.xticks(rotation=45)
plt.subplot(1, 2, 2)
sns.boxplot(x='Is_OC', y='Thickness', data=df_period_compare, palette='Pastel1')
plt.title('Natural Cycle vs OC Period')
plt.tight_layout()
plt.savefig('analysis_results.png')
plt.show()

summary_stats = df_analysis.groupby('Phase')['Thickness'].agg(['mean', 'std', 'count'])
summary_stats.to_csv('summary_statistics.csv')
