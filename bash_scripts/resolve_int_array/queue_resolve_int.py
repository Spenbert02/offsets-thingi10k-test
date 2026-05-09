from pathlib import Path
import subprocess


# ALL = 0  # run every single model
# UNSUCCESSFUL = 1  # run every model that hasn't already succeeded
# UNLOGGED = 2  # run every model that hasn't already been run (based off logs)

mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/resolve_int_array/pending_jobs.txt"
slurm_script_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/resolve_int_array/resolve_int_array.slurm"
# logs_dir = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test3_array/logs"

# RUN_MODE = UNLOGGED
CHUNK_SIZE = 1000
MAX_CHUNKS = None

def main():
    mesh_dir_path = Path(mesh_dir)
    if not (mesh_dir_path.exists() and mesh_dir_path.is_dir()):
        raise FileNotFoundError(f"{str(mesh_dir_path)} does not exist")
    
    # # collect already run models
    # log_dir_path = Path(logs_dir)
    # already_run = set()
    # for p in log_dir_path.iterdir():
    #     if not (p.is_file() and p.suffix.lower() == ".out"):
    #         continue
    #     try:
    #         model_id = int(p.stem.split("_")[1])
    #     except:
    #         print(f"WARNING: non-int-parseable log file at {str(log_dir_path)}")
    #         continue
    #     already_run.add(model_id)

    # collect jsons
    json_pairs_to_run = []
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        # if (RUN_MODE == UNLOGGED) and model_id in already_run:
        #     continue
        
        # input_obj_path = subdir / f"model_{model_id}.obj"
        # if not input_obj_path.exists():
        #     print(f"WARNING: no obj for model {model_id}")
        #     continue

        remesh_out_dir = mesh_dir_path / f"model_{model_id}" / "pair_remesh_test1"
        if not remesh_out_dir.exists():
            continue
        remesh_json_paths = list(remesh_out_dir.glob("*.json"))
        if (len(remesh_json_paths) != 1):
            print(f"WARNING: not one .json in {remesh_out_dir}")
            continue
        remesh_json_path = remesh_json_paths[0]

        resolve_int_out_dir = mesh_dir_path / f"model_{model_id}" / "pair_resolve_int_test1"
        resolve_int_json_paths = list(resolve_int_out_dir.glob("*.json"))
        if (len(resolve_int_json_paths) != 1):
            print(f"WARNING: not one .json in {resolve_int_out_dir}")
            continue
        resolve_int_json_path = resolve_int_json_paths[0]

        json_pairs_to_run.append([remesh_json_path, resolve_int_json_path])

    run_list_path = Path(run_list_fpath)
    
    num_jobs = len(json_pairs_to_run)
    print(f"Found {num_jobs} [remeshing_test3] jobs to run")
    chunks = [json_pairs_to_run[i:i + CHUNK_SIZE] for i in range(0, num_jobs, CHUNK_SIZE)]
    for idx, chunk in enumerate(chunks):
        if MAX_CHUNKS:
            if idx > (MAX_CHUNKS - 1):
                continue
        chunk_file = run_list_path.with_name(f"pending_jobs_{idx}.txt")
        with open(chunk_file, "w") as f:
            for json_pair in chunk:
                f.write(f"{json_pair[0]}\n")
                f.write(f"{json_pair[1]}\n")
        arr_max = len(chunk) - 1
        slurm_script_path = Path(slurm_script_fpath)
        sbatch_cmd = ["sbatch", f"--array=0-{arr_max}", "--mail-user=seb9449@nyu.edu", "--mail-type=BEGIN,END,FAIL,REQUEUE", str(slurm_script_path), str(chunk_file)]
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