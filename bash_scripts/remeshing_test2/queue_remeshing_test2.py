from pathlib import Path
import subprocess


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test2/pending_jobs.txt"
slurm_script_fpath = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test2/remeshing_test2_submit.slurm"
RERUN_ALL = True

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

    print(f"{successes} models already successfully ran through [remeshing_test2]. {len(jsons_to_run)} models to run.")
    run_list_path = Path(run_list_fpath)
    with open(run_list_fpath, "w") as f:
        for json_path in jsons_to_run:
            f.write(f"{json_path}\n")
    
    slurm_path = Path(slurm_script_fpath)
    sbatch_cmd =[
        "sbatch",
        "--mail-user=seb9449@nyu.edu",
        "--mail-type=BEGIN,END,FAIL",
        str(slurm_path),
        str(run_list_path)
    ]
    subprocess.run(sbatch_cmd, check=True)


if __name__ == "__main__":
    main()