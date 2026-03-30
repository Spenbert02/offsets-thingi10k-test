import argparse
from pathlib import Path
import subprocess
import time


def serial_process(mesh_dir, tetwild):
    mesh_dir_path = Path(mesh_dir)
    for subdir in mesh_dir_path.glob("model_*"):
        if subdir.exists() and subdir.is_dir():
            try:
                model_id = int(subdir.name.split("_")[1])
            except:
                print(f"WARNING: non integer model directory '{subdir.name}'")
                continue

            twild_subdir = subdir / "tetwild_output"
            twild_out_msh_path = twild_subdir / f"model_{model_id}_tetwild_output.msh"
            if twild_subdir.exists() and twild_out_msh_path.exists():
                print(f"Model {model_id} already processed.")
                continue

            obj_path = subdir / f"model_{model_id}.obj"
            if not obj_path.exists():
                print(f"Warning: model_{model_id}.obj does not exist")
                continue

            # clean out or create directory
            print(f"processing model {model_id}")
            if twild_subdir.exists():
                for p in twild_subdir.iterdir():
                    if p.is_file():
                        p.unlink()
            else:
                twild_subdir.mkdir(parents=True, exist_ok=True)

            command = [tetwild, "--input", str(obj_path), "--output", str(twild_out_msh_path.with_suffix("")), "--save-mid-result", "2"]
            start_time = time.time()
            result = subprocess.run(command)
            duration = int(time.time() - start_time)
            print(f"{model_id} execution finished in {duration}s with return code {result.returncode}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process unfinished meshes serially")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    parser.add_argument("-e", "--tetwild", required=True, help="Path to build TetWild executable")
    args = parser.parse_args()
    serial_process(args.meshdir, args.tetwild)
