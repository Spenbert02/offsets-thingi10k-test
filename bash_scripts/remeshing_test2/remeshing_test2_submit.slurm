#!/bin/bash
#SBATCH --job-name=remeshing_test2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --account=torch_pr_870_general
#SBATCH --output=logs/parallel_%A.out 
#SBATCH --error=logs/parallel_%A.err

eval "$(conda shell.bash hook)"
conda activate offsets_test_thingi10k

RUN_LIST=$1

run_model() {
    JSON_PATH=$1
    WMTK_EXE="/scratch/seb9449/wildmeshing-toolkit/build/app/wmtk_app"
    MODEL_NAME=$(echo "$JSON_PATH" | grep -oE 'model_[0-9]+' | head -n 1)
    
    # Execute the app and route the output to your named log file
    "$WMTK_EXE" -j "$JSON_PATH" > "logs/${MODEL_NAME}.out" 2>&1
}

export -f run_model

parallel    --jobs 0 \
            --load 100% \
            --delay 2 \
            --noswap \
            --joblog logs/task_history.log \
            "run_model {}" :::: "$RUN_LIST"
   