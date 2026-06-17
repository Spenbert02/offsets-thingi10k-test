#!/bin/bash
#SBATCH --job-name=model_106830_debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=1:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=logs/model_106830_debug.out 
#SBATCH --error=logs/model_106830_debug.err

export OMP_NUM_THREADS=1
export IGL_NUM_THREADS=1

# UPDATE THIS to match the base directory in your python script
JSON_PATH="/scratch/seb9449/offsets_testing_thingi10k/testbench/model_106830_debug/remeshing_test6_106830.json"
WMTK_EXE="/scratch/seb9449/debug_builds/wildmeshing-toolkit/build/app/wmtk_app"

# Execute remeshing
"$WMTK_EXE" -j "$JSON_PATH"