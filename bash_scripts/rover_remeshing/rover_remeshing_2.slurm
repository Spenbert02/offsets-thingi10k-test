#!/bin/bash
#SBATCH --job-name=rover_remesh_2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=256G
#SBATCH --time=168:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=logs/rover_remeshing_2.out 
#SBATCH --error=logs/rover_remeshing_2.err

export OMP_NUM_THREADS=32
export IGL_NUM_THREADS=32

# UPDATE THIS to match the base directory in your python script
JSON_PATH="/scratch/seb9449/offsets_testing_thingi10k/specific_models/rover/remeshing_rover.json"
WMTK_EXE="/scratch/seb9449/debug_builds/wildmeshing-toolkit/build/app/wmtk_app"

# Execute remeshing
"$WMTK_EXE" -j "$JSON_PATH"