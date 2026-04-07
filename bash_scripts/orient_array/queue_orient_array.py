from pathlib import Path
import subprocess


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/orient_array/pending_jobs.txt"
slurm_script_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/orient_array/orient_submit_array.slurm"
RERUN_ALL = False
CHUNK_SIZE = 1000


def main():
    mesh_dir_path = Path(mesh_dir)
    if not (mesh_dir_path.exists() and mesh_dir_path.is_dir()):
        raise FileNotFoundError(f"{str(mesh_dir_path)} does not exist")

    ids_to_orient = []
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        orient_out_dir = subdir / "orient_output"
        if not orient_out_dir.exists():
            orient_out_dir.mkdir(parents=True, exist_ok=True)
            ids_to_orient.append(model_id)
            continue

        orient_output = orient_out_dir / f"model_{model_id}_oriented.obj"
        if (not orient_output.exists()) or RERUN_ALL:
            ids_to_orient.append(model_id)
        
    print(f"{len(ids_to_orient)} models already oriented.")
    run_list_path = Path(run_list_fpath)
    num_jobs = len(ids_to_orient)
    print(f"Found {num_jobs} offset jobs to run")
    chunks = [ids_to_orient[i:i + CHUNK_SIZE] for i in range(0, num_jobs, CHUNK_SIZE)]
    for idx, chunk in enumerate(chunks):
        chunk_file = run_list_path.with_name(f"pending_jobs_{idx}.txt")
        with open(chunk_file, "w") as f:
            for json_path in chunk:
                f.write(f"{json_path}\n")
        arr_max = len(chunk) - 1
        slurm_script_path = Path(slurm_script_fpath)
        sbatch_cmd = ["sbatch", f"--array=0-{arr_max}", str(slurm_script_path), str(chunk_file)]
        print(f"Submitting chunk {idx+1}/{len(chunks)}: {' '.join(sbatch_cmd)}")
        try:
            subprocess.run(sbatch_cmd, check=True)
            print(f"Chunk {idx+1}/{len(chunks)} successfully committed to queue")
        except subprocess.CalledProcessError as e:
            print(f"Failed to submit chunk {idx}. Error: {e}")
            break
        except FileNotFoundError:
            print("Error: 'sbatch' command not found. Are you running this on the HPC login node?")
            break


if __name__ == "__main__":
    main()