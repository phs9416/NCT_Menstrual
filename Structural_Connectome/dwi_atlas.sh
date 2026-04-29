#!/bin/bash

# Number of parallel jobs
num_jobs=4 

export MNI_TEMPLATE="MNIspace.nii.gz" 
export PARCELLATION_TEMPLATE="Schaefer2018_100Parcels_7Networks_order_FSLMNI152_1mm.nii.gz" 

process_subject_phase() {
    local sub="$1"
    local phase="$2"
    local sub_anat="/home/phs9416/data/ds005360-download/${sub}/ses-0${phase}/anat"

    if [ ! -d "${sub_anat}" ]; then
        echo "Directory ${sub_anat} does not exist! Skipping..."
        return
    fi

    if [ ! -f "${sub_anat}/T1w_brain.nii.gz" ]; then
        echo "File ${sub_anat}/T1w_brain.nii.gz not found! Skipping..."
        return
    fi

    echo "Processing subject: ${sub}, phase: ${phase}..."

    # FLIRT (Linear registration)
    flirt -in "${sub_anat}/T1w_brain.nii.gz" -ref "${MNI_TEMPLATE}" \
          -out "${sub_anat}/T1w_lin_reg.nii" \
          -omat "${sub_anat}/T1w2MNI_linear.mat" -dof 6

    # FNIRT (Non-linear registration)
    fnirt --in="${sub_anat}/T1w_brain.nii.gz" \
          --aff="${sub_anat}/T1w2MNI_linear.mat" \
          --cout="${sub_anat}/T1w2MNI_nonlinear_coeff.nii.gz" \
          --ref="${MNI_TEMPLATE}"

    # INVWARP (Inverse warp)
    invwarp --warp="${sub_anat}/T1w2MNI_nonlinear_coeff.nii.gz" \
            --ref="${sub_anat}/T1w_brain.nii.gz" \
            --out="${sub_anat}/MNI2T1w_nonlinear_coeff.nii.gz"

    # Applywarp
    warpinit "${MNI_TEMPLATE}" "${sub_anat}/inv.nii"
    applywarp --ref="${sub_anat}/T1w_brain.nii.gz" \
              --in="${sub_anat}/inv.nii" \
              --warp="${sub_anat}/MNI2T1w_nonlinear_coeff.nii.gz" \
              --out="${sub_anat}/mrtrix_warp.nii.gz"

    # MRTRIX Transform
    mrtransform "${PARCELLATION_TEMPLATE}" \
                -warp "${sub_anat}/mrtrix_warp.nii.gz" \
                "${sub_anat}/schaefer2T1w.nii.gz" \
                -interp nearest 
    mrconvert "${sub_anat}/schaefer2T1w.nii.gz" "${sub_anat}/schaefer2T1w.mif"
}

export -f process_subject_phase

for phase in 1 2 3; do
    cat subjList.txt | parallel -j "${num_jobs}" process_subject_phase {} "${phase}"
done
