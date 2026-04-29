import pandas as pd
import numpy as np
import neurosynth as ns
import os
import nimare
from pathlib import Path
from nilearn import plotting
from nilearn.input_data import NiftiLabelsMasker
from nilearn._utils import check_niimg

data_dir = Path('/home/phs9416/data/neurosynth_data/data')
output_dir = Path('/home/phs9416/data/neurosynth_results')
output_dir.mkdir(parents=True, exist_ok=True)

# Neurosynth data loading
databases = nimare.extract.fetch_neurosynth(data_dir=str(data_dir))[0]
ds = nimare.io.convert_neurosynth_to_dataset(
    coordinates_file=databases['coordinates'],
    metadata_file=databases['metadata'],
    annotations_files=databases['features']
)

labels = ["LH_Vis_1", "LH_Vis_2", "LH_Vis_3", "LH_Vis_4", "LH_Vis_5", "LH_Vis_6", "LH_Vis_7", "LH_Vis_8", "LH_Vis_9",
        "LH_SomMot_1", "LH_SomMot_2", "LH_SomMot_3", "LH_SomMot_4", "LH_SomMot_5", "LH_SomMot_6", 
        "LH_DorsAttn_Post_1", "LH_DorsAttn_Post_2", "LH_DorsAttn_Post_3", "LH_DorsAttn_Post_4", "LH_DorsAttn_Post_5", 
        "LH_DorsAttn_Post_6", "LH_DorsAttn_PrCv_1", "LH_DorsAttn_FEF_1", 
        "LH_SalVentAttn_ParOper_1", "LH_SalVentAttn_FrOperIns_1", "LH_SalVentAttn_FrOperIns_2", "LH_SalVentAttn_PFCl_1",
        "LH_SalVentAttn_Med_1", "LH_SalVentAttn_Med_2", "LH_SalVentAttn_Med_3",
        "LH_Limbic_OFC_1", "LH_Limbic_TempPole_1", "LH_Limbic_TempPole_2",
        "LH_Cont_Par_1", "LH_Cont_PFCl_1", "LH_Cont_pCun_1", "LH_Cont_Cing_1",
        "LH_Default_Temp_1", "LH_Default_Temp_2", "LH_Default_Par_1", "LH_Default_Par_2", 
        "LH_Default_PFC_1", "LH_Default_PFC_2", "LH_Default_PFC_3", "LH_Default_PFC_4", "LH_Default_PFC_5", "LH_Default_PFC_6",
        "LH_Default_PFC_7", "LH_Default_pCunPCC_1", "LH_Default_pCunPCC_2",
        "RH_Vis_1", "RH_Vis_2", "RH_Vis_3", "RH_Vis_4", "RH_Vis_5", "RH_Vis_6", "RH_Vis_7", "RH_Vis_8",
        "RH_SomMot_1", "RH_SomMot_2", "RH_SomMot_3", "RH_SomMot_4", "RH_SomMot_5", "RH_SomMot_6", "RH_SomMot_7", "RH_SomMot_8",
        "RH_DorsAttn_Post_1", "RH_DorsAttn_Post_2", "RH_DorsAttn_Post_3", "RH_DorsAttn_Post_4", "RH_DorsAttn_Post_5", "RH_DorsAttn_PrCv_1",
        "RH_DorsAttn_FEF_1", "RH_SalVentAttn_TempOccPar_1",
        "RH_SalVentAttn_TempOccPar_2", "RH_SalVentAttn_FrOperIns_1", "RH_SalVentAttn_Med_1", "RH_SalVentAttn_Med_2",
        "RH_Limbic_OFC_1", "RH_Limbic_TempPole_1", "RH_Cont_Par_1", "RH_Cont_Par_2",
        "RH_Cont_PFCl_1", "RH_Cont_PFCl_2", "RH_Cont_PFCl_3", "RH_Cont_PFCl_4", "RH_Cont_Cing_1", "RH_Cont_PFCmp_1",
        "RH_Cont_pCun_1", "RH_Default_Par_1", "RH_Default_Temp_1", "RH_Default_Temp_2", "RH_Default_Temp_3",
        "RH_Default_PFCv_1", "RH_Default_PFCv_2", "RH_Default_PFCdPFCm_1", "RH_Default_PFCdPFCm_2", "RH_Default_PFCdPFCm_3",
        "RH_Default_pCunPCC_1", "RH_Default_pCunPCC_2"
        ]

term_list = [
    'action', 'adaptation', 'addiction', 'anticipation', 'anxiety',
    'arousal', 'association', 'attention', 'autobiographical memory', 'balance',
    'belief', 'categorization', 'cognitive control', 'communication', 'competition',
    'concept', 'consciousness', 'consolidation', 'context', 'coordination',
    'decision', 'decision making', 'detection', 'discrimination', 'distraction',
    'eating', 'efficiency', 'effort', 'emotion', 'emotion regulation',
    'empathy', 'encoding', 'episodic memory', 'expectancy', 'expertise',
    'extinction', 'face recognition', 'facial expression', 'familiarity', 'fear',
    'fixation', 'focus', 'gaze', 'goal', 'hyperactivity',
    'imagery', 'impulsivity', 'induction', 'inference', 'inhibition',
    'insight', 'integration', 'intelligence', 'intention', 'interference',
    'judgment', 'knowledge', 'language', 'language comprehension', 'learning',
    'listening', 'localization', 'loss', 'maintenance', 'manipulation',
    'meaning', 'memory', 'memory retrieval', 'mental imagery', 'monitoring',
    'mood', 'morphology', 'motor control', 'movement', 'multisensory',
    'naming', 'navigation', 'object recognition', 'pain', 'perception',
    'planning', 'priming', 'psychosis', 'reading', 'reasoning',
    'recall', 'recognition', 'rehearsal', 'reinforcement learning', 'response inhibition',
    'response selection', 'retention', 'retrieval', 'reward anticipation', 'rhythm',
    'risk', 'rule', 'salience', 'search', 'selective attention',
    'semantic memory', 'sentence comprehension', 'skill', 'sleep', 'social cognition',
    'spatial attention', 'speech perception', 'speech production', 'strategy', 'strength',
    'stress', 'sustained attention', 'task difficulty', 'thought', 'uncertainty',
    'updating', 'utility', 'valence', 'verbal fluency', 'visual attention',
    'visual perception', 'word recognition', 'working memory'
]

prefixed_terms = [f"terms_abstract_tfidf__{term}" for term in term_list]

for term in prefixed_terms:
    try:
        term_name = term.split('__')[1]
        print(f"▶ Processing term: {term_name}")

        term_ids = ds.get_studies_by_label(labels=term, label_threshold=0.001)
        if len(term_ids) < 5:
            print(f"  ⤷ skip due to few study ({len(term_ids)})")
            continue

        notterm_ids = sorted(list(set(ds.ids) - set(term_ids)))
        term_dset = ds.slice(term_ids)
        notterm_dset = ds.slice(notterm_ids)

        meta = nimare.meta.cbma.mkda.MKDAChi2()
        results = meta.fit(term_dset, notterm_dset)
        results.save_maps(output_dir=output_dir, prefix=term_name)

        corrector = nimare.correct.FDRCorrector(alpha=0.01)
        results_corrected = corrector.transform(results)
        results_corrected.save_maps(output_dir=output_dir, prefix=term_name)

    except Exception as e:
        print(f"  ⤷ error: {e}")
        continue

print("✅ completed.")


data = pd.DataFrame(index=labels)
atlas = '/home/phs9416/data/Schaefer2018_100Parcels_7Networks_order_FSLMNI152_1mm.nii.gz'
mask = NiftiLabelsMasker(atlas, resampling_target='data')
map_dir = '/home/phs9416/UKB_NCT/neurosynth_data/neurosynth_results'

# parcellation
for term in term_list:
    nii_file = os.path.join(map_dir, f'{term}_z_desc-association_level-voxel_corr-FDR_method-indep.nii.gz')
    if os.path.exists(nii_file):
        print(f'Processing: {term}')
        img = check_niimg(nii_file, atleast_4d=True)
        vec = mask.fit_transform(img).squeeze()
        data[term] = vec
    else:
        print(f'File not found: {nii_file}')
        data[term] = np.nan 

data.to_csv('/home/phs9416/data/top123_S100.csv', sep=',')
