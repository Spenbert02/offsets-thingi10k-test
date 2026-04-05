from pathlib import Path
import subprocess


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/offsets_array/pending_jobs.txt"
slurm_script_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/offsets_array/offset_submit_array.slurm"
RERUN_ALL = False

def main():
    mesh_dir_path = Path(mesh_dir)
    if not (mesh_dir_path.exists() and mesh_dir_path.is_dir()):
        raise FileNotFoundError(f"{str(mesh_dir_path)} does not exist")

    jsons_to_run = []
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        input_msh_path = subdir / "tetwild_output" / f"model_{model_id}_tetwild_output_retagged.msh"
        if not input_msh_path.exists():
            print(f"WARNING: no retagged tetwild output for model {model_id}")
            continue

        singlebody_output_msh_path = subdir / "singlebody" / f"model_{model_id}_singlebody_offset_output.msh"
        if singlebody_output_msh_path.exists() and not RERUN_ALL:
            print(f"Model {model_id} (single body) already succesfully offset.")
        else:
            singlebody_json_path = subdir / "singlebody" / f"singlebody_{model_id}_offset.json"
            if not singlebody_json_path.exists():
                print(f"WARNING: singlebody json {str(singlebody_json_path)} does not exist")
            else:
                jsons_to_run.append(str(singlebody_json_path))
        
        twobody_output_msh_path = subdir / "twobody" / f"model_{model_id}_twobody_offset_output.msh"
        if twobody_output_msh_path.exists() and not RERUN_ALL:
            print(f"Model {model_id} (two body) already succesfully offset.")
        else:
            twobody_json_path = subdir / "twobody" / f"twobody_{model_id}_offset.json"
            if not twobody_json_path.exists():
                print(f"WARNING: twobody json {str(twobody_json_path)} does not exist")
            else:
                jsons_to_run.append(str(twobody_json_path))

    run_list_path = Path(run_list_fpath)
    with open(str(run_list_path), "w") as f:
        for json_fpath in jsons_to_run:
            f.write(f"{json_fpath}\n")
    
    num_jobs = len(jsons_to_run)
    print(f"Found {num_jobs} offset jobs to run")

    slurm_script_path = Path(slurm_script_fpath)
    sbatch_cmd = ["sbatch", f"--array=0-{num_jobs - 1}", str(slurm_script_path), str(run_list_path)]
    print(f"Submitting SLURM array: {' '.join(sbatch_cmd)}")
    try:
        subprocess.run(sbatch_cmd, check=True)
        print("Offset jobs successfully committed to queue")
    except subprocess.CalledProcessError as e:
        print(f"Failed to submit jobs. Error: {e}")
    except FileNotFoundError:
        print("Error: 'sbatch' command not found. Are you running this on the HPC login node?")


if __name__ == "__main__":
    main()