#!/bin/bash
#SBATCH --job-name=offsets_sweep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=1:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=logs/job_%A_%a.out 
#SBATCH --error=logs/job_%A_%a.err

# UPDATE THIS to match the base directory in your python script
BASE_DIR="/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
OFFSETS_EXE="/scratch/seb9449/wildmeshing-toolkit/build/app/wmtk_app"

RUN_LIST=$1

# Grab the exact model name for this specific array task (e.g., "model_42")
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
JSON_PATH=$(sed -n "${LINE_NUM}p" "$RUN_LIST")

echo "=========================================="
echo "Task ID: $SLURM_ARRAY_TASK_ID"
echo "Processing JSON: $JSON_PATH"
echo "=========================================="

# Execute offsets
$OFFSETS_EXE -j $JSON_PATH