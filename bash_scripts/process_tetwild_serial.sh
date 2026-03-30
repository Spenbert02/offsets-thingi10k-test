#!/bin/bash
#SBATCH --job-name=tetwild_processing
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=tetwild_output_%j.out  # This captures your print statements/progress bar

module purge
module load anaconda3/2025.06
source /share/apps/anaconda3/2025.06/etc/profile.d/conda.sh
export PATH_TO_ENV=$SCRATCH/conda/envs/offsets_test_thingi10k
source activate $PATH_TO_ENV
python -u $SCRATCH/offsets_testing_thingi10k/offsets-thingi10k-test/python_scripts/serial_tetwild_process.py -m $SCRATCH/offsets_testing_thingi10k/tagged_tet_mshes -e $SCRATCH/TetWild/build/TetWild