#!/bin/bash
#SBATCH --job-name=tetwild_sweep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=12:00:00           
#SBATCH --output=logs/job_%A_%a.out 
#SBATCH --error=logs/job_%A_%a.err

# UPDATE THIS to match the base directory in your python script
BASE_DIR="/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
TETWILD_EXE="/scratch/seb9449/TetWild/build/TetWild"

RUN_LIST=$1

# Grab the exact model name for this specific array task (e.g., "model_42")
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
MODEL_ID=$(sed -n "${LINE_NUM}p" "$RUN_LIST")

# Construct the exact paths requested
INPUT_OBJ="${BASE_DIR}/model_${MODEL_ID}/model_${MODEL_ID}.obj"
OUT_DIR="${BASE_DIR}/model_${MODEL_ID}/tetwild_output"
OUTPUT_PREFIX="${OUT_DIR}/model_${MODEL_ID}_tetwild_output"

echo "=========================================="
echo "Task ID: $SLURM_ARRAY_TASK_ID"
echo "Processing: model $MODEL_ID"
echo "Input: $INPUT_OBJ"
echo "Output Prefix: $OUTPUT_PREFIX"
echo "=========================================="

# Execute TetWild
$TETWILD_EXE --input "$INPUT_OBJ" --output "$OUTPUT_PREFIX" --save-mid-result 2