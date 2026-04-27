from pathlib import Path
import subprocess


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test2_array/pending_jobs.txt"
slurm_script_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test2_array/remeshing_test2_submit_array.slurm"
RERUN_ALL = False
CHUNK_SIZE = 10000

def main():
    mesh_dir_path = Path(mesh_dir)
    if not (mesh_dir_path.exists() and mesh_dir_path.is_dir()):
        raise FileNotFoundError(f"{str(mesh_dir_path)} does not exist")

    jsons_to_run = []
    successes = 0
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue
        
        input_obj_path = subdir / f"model_{model_id}.obj"
        if not input_obj_path.exists():
            print(f"WARNING: no obj for model {model_id}")
            continue

        output_msh_path = subdir / "remeshing_test2" / f"model_{model_id}_out.msh"
        if output_msh_path.exists() and not RERUN_ALL:
            successes += 1
        else:
            json_path = subdir / "remeshing_test2" / f"remeshing_test2_{model_id}.json"
            if not json_path.exists():
                print(f"WARNING: json {str(json_path)} does not exist")
            else:
                jsons_to_run.append(str(json_path))

    print(f"{successes} models already successfully ran through [remeshing_test2].")
    run_list_path = Path(run_list_fpath)
    
    num_jobs = len(jsons_to_run)
    print(f"Found {num_jobs} [remeshing_test2] jobs to run")
    chunks = [jsons_to_run[i:i + CHUNK_SIZE] for i in range(0, num_jobs, CHUNK_SIZE)]
    for idx, chunk in enumerate(chunks):
        chunk_file = run_list_path.with_name(f"pending_jobs_{idx}.txt")
        with open(chunk_file, "w") as f:
            for json_path in chunk:
                f.write(f"{json_path}\n")
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