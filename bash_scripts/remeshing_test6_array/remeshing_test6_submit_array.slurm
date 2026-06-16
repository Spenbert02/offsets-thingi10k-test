#!/bin/bash
#SBATCH --job-name=remeshing_test5_sweep1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=128G
#SBATCH --time=48:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=logs/job_%A_%a.out 
#SBATCH --error=logs/job_%A_%a.err

export OMP_NUM_THREADS=1
export IGL_NUM_THREADS=1

# UPDATE THIS to match the base directory in your python script
BASE_DIR="/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
WMTK_EXE="/scratch/seb9449/wildmeshing-toolkit/build/app/wmtk_app"

RUN_LIST=$1

# Grab the json path
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
JSON_PATH=$(sed -n "${LINE_NUM}p" "$RUN_LIST")

echo "=========================================="
echo "Task ID: $SLURM_ARRAY_TASK_ID"
echo "Processing JSON: $JSON_PATH"
echo "=========================================="

# Execute offsets
taskset -c $(taskset -cp $$ | cut -d: -f2 | xargs) "$WMTK_EXE" -j "$JSON_PATH"