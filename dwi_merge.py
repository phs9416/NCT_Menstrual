import os
import nibabel as nib
import numpy as np

# Step 1: subJList.txt에서 subject ID 읽기
with open("subjList.txt", "r") as f:
    subjects = [line.strip() for line in f.readlines()]

# Step 2: 각 subject와 세션에 대해 파일 병합
base_dir = "/u7/phs9416/hhs/ds005360-download/"  # 데이터의 루트 디렉토리
for subject in subjects:
    subject_dir = os.path.join(base_dir, subject)
    sessions = [d for d in os.listdir(subject_dir) if d.startswith("ses-")]

    for session in sessions:
        session_dir = os.path.join(subject_dir, session, "dwi")
        
        # NIfTI, bval, bvec 파일 탐색
        nifti_files = sorted([os.path.join(session_dir, f) for f in os.listdir(session_dir) if f.endswith(".nii")])
        bval_files = sorted([os.path.join(session_dir, f) for f in os.listdir(session_dir) if f.endswith(".bval")])
        bvec_files = sorted([os.path.join(session_dir, f) for f in os.listdir(session_dir) if f.endswith(".bvec")])

        # NIfTI 파일 병합
        nifti_images = [nib.load(f) for f in nifti_files]
        nifti_data = np.concatenate([img.get_fdata() for img in nifti_images], axis=-1)
        merged_affine = nifti_images[0].affine
        merged_nifti = nib.Nifti1Image(nifti_data, merged_affine)
        merged_nifti_filename = os.path.join(session_dir, f"{session}_merged_dwi.nii.gz")
        merged_nifti.to_filename(merged_nifti_filename)

        # bval 파일 병합
        merged_bvals = []
        for bval_file in bval_files:
            with open(bval_file, "r") as f:
                bvals = f.read().strip().split()
                merged_bvals.extend(bvals)
        merged_bval_filename = os.path.join(session_dir, f"{session}_merged_dwi.bval")
        with open(merged_bval_filename, "w") as f:
            f.write(" ".join(merged_bvals) + "\n")

        # bvec 파일 병합
        merged_bvecs = [[], [], []]
        for bvec_file in bvec_files:
            with open(bvec_file, "r") as f:
                bvec_lines = f.readlines()
                for i in range(3):
                    merged_bvecs[i].extend(bvec_lines[i].strip().split())
        merged_bvec_filename = os.path.join(session_dir, f"{session}_merged_dwi.bvec")
        with open(merged_bvec_filename, "w") as f:
            for i in range(3):
                f.write(" ".join(merged_bvecs[i]) + "\n")

        print(f"Merged files saved for {subject} {session}.")
