#!/bin/bash
#SBATCH --job-name=offsets_90979_2body
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=4:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=logs/job_%j_0.out 
#SBATCH --error=logs/job_%j_0.err

OFFSETS_EXE="/scratch/seb9449/wildmeshing-toolkit/build/app/wmtk_app"
JSON_PATH="/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes/model_90979/twobody/twobody_90979_offset.json"

echo "=========================================="
echo "Task ID: 0"
echo "Processing JSON: $JSON_PATH"
echo "=========================================="

# Execute offsets
$OFFSETS_EXE -j $JSON_PATH