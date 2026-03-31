import argparse
from pathlib import Path
import json


def populate_jsons(meshes_dir):
    msh_dir_path = Path(meshes_dir)
    if not msh_dir_path.exists():
        raise FileNotFoundError(str(msh_dir_path))

    count = 0
    for subdir in msh_dir_path.glob("model_*"):
        if subdir.exists() and subdir.is_dir():
            try:
                model_id = int(subdir.name.split("_")[1])
            except:
                print(f"WARNING: non int dir name: {subdir.name}")
                continue
            
            twild_output_dir = subdir / "tetwild_output"
            if not (twild_output_dir.exists() and twild_output_dir.is_dir()):
                print(f"WARNING: 'tetwild_output' directory does not exist for model_{model_id}")

            input_msh_path = twild_output_dir / f"model_{model_id}_tetwild_output_retagged.msh"
            if not input_msh_path.exists():
                print(f"WARNING: '{input_msh_path}' does not exist in 'tetwild_output' directory")

            single_subdir = subdir / f"singlebody"
            single_subdir.mkdir(parents=True, exist_ok=True)
            single_json_path = single_subdir / f"singlebody_{model_id}_offset.json"
            single_data = {
                "application": "topological_offset",
                "input": str(input_msh_path),
                "output": f"model_{model_id}_singlebody_offset_output",
                "offset_tags": [ [0, 0] ],
                "offset_tag_val": [ [0, 2] ],
                "target_distance": 1.0,
                "relative_ball_threshold": 0.01,
                "save_vtu": False,
                "DEBUG_output": False,
                "sorted_marching": False,
                "check_manifoldness": True
            }
            with open(single_json_path, "w") as f:
                json.dump(single_data, f, indent=4)

            twobody_subdir = subdir / f"twobody"
            twobody_subdir.mkdir(parents=True, exist_ok=True)
            twobody_json_path = twobody_subdir / f"twobody_{model_id}_offset.json"
            twobody_data = {
                "application": "topological_offset",
                "input": str(input_msh_path),
                "output": f"model_{model_id}_twobody_offset_output",
                "offset_tags": [ [0, 0], [0, 1] ],
                "offset_tag_val": [ [0, 2] ],
                "target_distance": 1.0,
                "relative_ball_threshold": 0.01,
                "save_vtu": False,
                "DEBUG_output": False,
                "sorted_marching": False,
                "check_manifoldness": True
            }
            with open(twobody_json_path, "w") as f:
                json.dump(twobody_data, f, indent=4)
            
            count += 2
    print(f"Created {count} jsons.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create jsons for offsets")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    args = parser.parse_args()
    populate_jsons(args.meshdir)
