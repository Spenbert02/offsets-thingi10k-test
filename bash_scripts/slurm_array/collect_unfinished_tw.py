from pathlib import Path
import subprocess


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/slurm_array/pending_jobs.txt"
slurm_script_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/slurm_array/submit_array.slurm"


def main():
    mesh_dir_path = Path(mesh_dir)
    if not (mesh_dir_path.exists() and mesh_dir_path.is_dir()):
        raise FileNotFoundError(f"{str(mesh_dir_path)} does not exist")
    
    pending_model_ids = []
    for subdir in mesh_dir_path.glob("model_*"):
        if not(subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        twild_out_dir = subdir / "tetwild_output"
        if not twild_out_dir.exists():
            twild_out_dir.mkdir(parents=True, exist_ok=False)
            pending_model_ids.append(model_id)
            continue

        out_msh_path = twild_out_dir / f"model_{model_id}_tetwild_output.msh"
        if not out_msh_path.exists():
            pending_model_ids.append(model_id)

    run_list_path = Path(run_list_fpath)
    with open(str(run_list_path), "w") as f:
        for model_id in pending_model_ids:
            f.write(f"{model_id}\n")
    
    num_jobs = len(pending_model_ids)
    print(f"Found {num_jobs} jobs need to run.")
    
    slurm_script_path = Path(slurm_script_fpath)
    sbatch_cmd = ["sbatch", f"--array=0-{num_jobs - 1}", str(slurm_script_path), str(run_list_path)]
    print(f"Submitting SLURM array: {' '.join(sbatch_cmd)}")
    try:
        subprocess.run(sbatch_cmd, check=True)
        print("Jobs successfully committed to queue")
    except subprocess.CalledProcessError as e:
        print(f"Failed to submit jobs. Error: {e}")
    except FileNotFoundError:
        print("Error: 'sbatch' command not found. Are you running this on the HPC login node?")


if __name__ == "__main__":
    main()