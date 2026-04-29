#!/bin/bash

cd /u7/phs9416/hhs/ds005360-download/

# for_each -nthreads 22 * : dwidenoise IN/ses-01/dwi/ses-01_dwi.mif IN/ses-01/dwi/ses-01_dwi_denoised.mif
# for_each -nthreads 22 * : dwidenoise IN/ses-02/dwi/ses-02_dwi.mif IN/ses-02/dwi/ses-02_dwi_denoised.mif
# for_each -nthreads 22 * : dwidenoise IN/ses-03/dwi/ses-03_dwi.mif IN/ses-03/dwi/ses-03_dwi_denoised.mif

# for_each -nthreads 22 * : mrdegibbs IN/ses-01/dwi/ses-01_dwi_denoised.mif IN/ses-01/dwi/dwi.mif -axes 0,1
# for_each -nthreads 22 * : mrdegibbs IN/ses-02/dwi/ses-02_dwi_denoised.mif IN/ses-02/dwi/dwi.mif -axes 0,1
# for_each -nthreads 22 * : mrdegibbs IN/ses-03/dwi/ses-03_dwi_denoised.mif IN/ses-03/dwi/dwi.mif -axes 0,1
 
# for_each -nthreads 22 * : rm IN/ses-01/dwi/ses-01_dwi_denoised.mif IN/ses-01/dwi/ses-01_dwi.mif IN/ses-01/dwi/ses-01_merged_dwi.nii.gz IN/ses-01/dwi/ses-01_merged_dwi.bvec IN/ses-01/dwi/ses-01_merged_dwi.bval
# for_each -nthreads 22 * : rm IN/ses-02/dwi/ses-02_dwi_denoised.mif IN/ses-02/dwi/ses-02_dwi.mif IN/ses-02/dwi/ses-02_merged_dwi.nii.gz IN/ses-02/dwi/ses-02_merged_dwi.bvec IN/ses-02/dwi/ses-02_merged_dwi.bval
# for_each -nthreads 22 * : rm IN/ses-03/dwi/ses-03_dwi_denoised.mif IN/ses-03/dwi/ses-03_dwi.mif IN/ses-03/dwi/ses-03_merged_dwi.nii.gz IN/ses-03/dwi/ses-03_merged_dwi.bvec IN/ses-03/dwi/ses-03_merged_dwi.bval

# for_each -nthreads 22 * : dwi2mask IN/ses-01/dwi/dwi.mif IN/ses-01/dwi/dwi_mask.mif
# for_each -nthreads 22 * : dwi2mask IN/ses-02/dwi/dwi.mif IN/ses-02/dwi/dwi_mask.mif
# for_each -nthreads 22 * : dwi2mask IN/ses-03/dwi/dwi.mif IN/ses-03/dwi/dwi_mask.mif

# for_each -nthreads 22 * : 5ttgen fsl IN/ses-01/anat/T1w_brain.nii.gz IN/ses-01/anat/5TT.mif -premasked
# for_each -nthreads 22 * : 5ttgen fsl IN/ses-02/anat/T1w_brain.nii.gz IN/ses-02/anat/5TT.mif -premasked
# for_each -nthreads 22 * : 5ttgen fsl IN/ses-03/anat/T1w_brain.nii.gz IN/ses-03/anat/5TT.mif -premasked
 
# for_each -nthreads 22 * : dwi2response msmt_5tt IN/ses-01/dwi/dwi.mif IN/ses-01/anat/5TT.mif IN/ses-01/dwi/wm.txt IN/ses-01/dwi/gm.txt IN/ses-01/dwi/csf.txt
# for_each -nthreads 22 * : dwi2response msmt_5tt IN/ses-02/dwi/dwi.mif IN/ses-02/anat/5TT.mif IN/ses-02/dwi/wm.txt IN/ses-02/dwi/gm.txt IN/ses-02/dwi/csf.txt
# for_each -nthreads 22 * : dwi2response msmt_5tt IN/ses-03/dwi/dwi.mif IN/ses-03/anat/5TT.mif IN/ses-03/dwi/wm.txt IN/ses-03/dwi/gm.txt IN/ses-03/dwi/csf.txt

# for_each -nthreads 22 * : dwi2fod msmt_csd IN/ses-01/dwi/dwi.mif IN/ses-01/dwi/wm.txt IN/ses-01/dwi/wm.mif IN/ses-01/dwi/gm.txt IN/ses-01/dwi/gm.mif IN/ses-01/dwi/csf.txt IN/ses-01/dwi/csf.mif -mask IN/ses-01/dwi/dwi_mask.mif
# for_each -nthreads 22 * : dwi2fod msmt_csd IN/ses-02/dwi/dwi.mif IN/ses-02/dwi/wm.txt IN/ses-02/dwi/wm.mif IN/ses-02/dwi/gm.txt IN/ses-02/dwi/gm.mif IN/ses-02/dwi/csf.txt IN/ses-02/dwi/csf.mif -mask IN/ses-02/dwi/dwi_mask.mif
# for_each -nthreads 22 * : dwi2fod msmt_csd IN/ses-03/dwi/dwi.mif IN/ses-03/dwi/wm.txt IN/ses-03/dwi/wm.mif IN/ses-03/dwi/gm.txt IN/ses-03/dwi/gm.mif IN/ses-03/dwi/csf.txt IN/ses-03/dwi/csf.mif -mask IN/ses-03/dwi/dwi_mask.mif

# for_each -nthreads 22 * : mtnormalise IN/ses-01/dwi/wm.mif IN/ses-01/dwi/wm_norm.mif IN/ses-01/dwi/gm.mif IN/ses-01/dwi/gm_norm.mif IN/ses-01/dwi/csf.mif IN/ses-01/dwi/csf_norm.mif -mask IN/ses-01/dwi/dwi_mask.mif
# for_each -nthreads 22 * : mtnormalise IN/ses-02/dwi/wm.mif IN/ses-02/dwi/wm_norm.mif IN/ses-02/dwi/gm.mif IN/ses-02/dwi/gm_norm.mif IN/ses-02/dwi/csf.mif IN/ses-02/dwi/csf_norm.mif -mask IN/ses-02/dwi/dwi_mask.mif
# for_each -nthreads 22 * : mtnormalise IN/ses-03/dwi/wm.mif IN/ses-03/dwi/wm_norm.mif IN/ses-03/dwi/gm.mif IN/ses-03/dwi/gm_norm.mif IN/ses-03/dwi/csf.mif IN/ses-03/dwi/csf_norm.mif -mask IN/ses-03/dwi/dwi_mask.mif

# for_each -nthreads 22 * : mrconvert IN/ses-01/dwi/wm_norm.mif - -coord 3 0 # | mrcat IN/ses-01/dwi/csf_norm.mif IN/ses-01/dwi/gm_norm.mif - IN/ses-01/dwi/tissueRGB.mif -axis 3
# for_each -nthreads 22 * : mrconvert IN/ses-02/dwi/wm_norm.mif - -coord 3 0 # | mrcat IN/ses-02/dwi/csf_norm.mif IN/ses-02/dwi/gm_norm.mif - IN/ses-02/dwi/tissueRGB.mif -axis 3
# for_each -nthreads 22 * : mrconvert IN/ses-03/dwi/wm_norm.mif - -coord 3 0 # | mrcat IN/ses-03/dwi/csf_norm.mif IN/ses-03/dwi/gm_norm.mif - IN/ses-03/dwi/tissueRGB.mif -axis 3

# for_each -nthreads 22 * : tckgen IN/ses-01/dwi/wm_norm.mif IN/ses-01/dwi/20M.tck -act IN/ses-01/anat/5TT.mif -backtrack -crop_at_gmwmi -seed_dynamic IN/ses-01/dwi/wm_norm.mif -maxlength 250 -select 20M -cutoff 0.06
# for_each -nthreads 22 * : tckgen IN/ses-02/dwi/wm_norm.mif IN/ses-02/dwi/20M.tck -act IN/ses-02/anat/5TT.mif -backtrack -crop_at_gmwmi -seed_dynamic IN/ses-02/dwi/wm_norm.mif -maxlength 250 -select 20M -cutoff 0.06
# for_each -nthreads 22 * : tckgen IN/ses-03/dwi/wm_norm.mif IN/ses-03/dwi/20M.tck -act IN/ses-03/anat/5TT.mif -backtrack -crop_at_gmwmi -seed_dynamic IN/ses-03/dwi/wm_norm.mif -maxlength 250 -select 20M -cutoff 0.06

# for_each -nthreads 22 * : tcksift IN/ses-01/dwi/20M.tck IN/ses-01/dwi/wm_norm.mif IN/ses-01/dwi/2M_SIFT.tck -act IN/ses-01/anat/5TT.mif -term_number 2M
# for_each -nthreads 22 * : tcksift IN/ses-02/dwi/20M.tck IN/ses-02/dwi/wm_norm.mif IN/ses-02/dwi/2M_SIFT.tck -act IN/ses-02/anat/5TT.mif -term_number 2M
# for_each -nthreads 22 * : tcksift IN/ses-03/dwi/20M.tck IN/ses-03/dwi/wm_norm.mif IN/ses-03/dwi/2M_SIFT.tck -act IN/ses-03/anat/5TT.mif -term_number 2M

# for_each -nthreads 22 * : tck2connectome IN/ses-01/dwi/2M_SIFT.tck IN/ses-01/anat/nodes_DK_fixSGM.mif ../connectome/ses-01/IN.csv
# for_each -nthreads 22 * : tck2connectome IN/ses-02/dwi/2M_SIFT.tck IN/ses-02/anat/nodes_DK_fixSGM.mif ../connectome/ses-02/IN.csv
# for_each -nthreads 22 * : tck2connectome IN/ses-03/dwi/2M_SIFT.tck IN/ses-03/anat/nodes_DK_fixSGM.mif ../connectome/ses-03/IN.csv

# for_each -nthreads 22 * : dwiextract -bzero IN/ses-01/dwi/dwi.mif IN/ses-01/dwi/dwi_bzero.mif 
# for_each -nthreads 22 * : mrmath IN/ses-01/dwi/dwi_bzero.mif mean IN/ses-01/dwi/mean_bzero.mif -axis 3
# for_each -nthreads 22 * : rm IN/ses-01/dwi/dwi_bzero.mif
# for_each -nthreads 22 * : dwiextract -bzero IN/ses-02/dwi/dwi.mif IN/ses-02/dwi/dwi_bzero.mif 
# for_each -nthreads 22 * : mrmath IN/ses-02/dwi/dwi_bzero.mif mean IN/ses-02/dwi/mean_bzero.mif -axis 3
# for_each -nthreads 22 * : rm IN/ses-02/dwi/dwi_bzero.mif
# for_each -nthreads 22 * : dwiextract -bzero IN/ses-03/dwi/dwi.mif IN/ses-03/dwi/dwi_bzero.mif 
# for_each -nthreads 22 * : mrmath IN/ses-03/dwi/dwi_bzero.mif mean IN/ses-03/dwi/mean_bzero.mif -axis 3
# for_each -nthreads 22 * : rm IN/ses-03/dwi/dwi_bzero.mif

# for_each -nthreads 22 * : mrconvert IN/ses-01/dwi/mean_bzero.mif IN/ses-01/dwi/mean_bzero.nii.gz
# for_each -nthreads 22 * : mrconvert IN/ses-02/dwi/mean_bzero.mif IN/ses-02/dwi/mean_bzero.nii.gz
# for_each -nthreads 22 * : mrconvert IN/ses-03/dwi/mean_bzero.mif IN/ses-03/dwi/mean_bzero.nii.gz







