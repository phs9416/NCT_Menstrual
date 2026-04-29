This repository contains the analysis code for the study investigating how hormonal fluctuations across the menstrual cycle and oral contraceptive use modulate brain state transition energy using Network Control Theory (NCT).  

# Repository Structure

## 1. Structural_Connectome
This directory contains scripts for reconstructing phase-specific structural connectomes from the Hormone Health Study (HHS) dataset.

  dwi_merge.py: Merges multidimensional diffusion MRI (dwi) data into a single file.
  
  dwi_atlas.sh: Registers the Schaefer 100-parcel atlas onto T1-weighted images for consistent node definition.
  
  dwi_work.sh: Generates individual structural connectomes for each subject across three menstrual phases

## 2. Control_Energy_Trajectory
Scripts in this folder analyze day-by-day control energy fluctuations using the longitudinal 28andMe dataset.  

  Control_Energy_Calculation.py: Computes day-by-day optimal control energy for different connectome groups (Groups A–D).  

  Connectome_Comparison.py: Performs statistical comparisons of control energy trajectories between connectome configurations.  

  Day_by_Day_SR_Gradient.py: Calculates trajectories based on different control sets (uniform vs. cortical thickness-weighted) and compares natural cycle variability against the oral contraceptive (OC) stabilized baseline. 

## 3. Cognitive_State_Transition
This section focuses on the energetic costs associated with 123 meta-analytic cognitive states derived from Neurosynth.  

  Cognitive_State_Extraction.py: Extracts spatial activation maps for 123 cognitive terms.  

  Inbound_Outbound.py: Quantifies Inbound Energy (cost to reach a state) and Outbound Energy (cost to exit a state).  

  Cognitive_State_ANOVA.py: Performs repeated-measures ANOVA (rm-ANOVA) to identify cognitive states significantly modulated by menstrual phase.  

  Cognitive_State_Clustering.py: Implements K-means clustering on energy delta trajectories to identify phase-dominant functional profiles. 
