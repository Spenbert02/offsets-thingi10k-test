from pathlib import Path
import json

meshes_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"

def main():
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

            union_subdir = subdir / f"manifold_union"
            union_subdir.mkdir(parents=True, exist_ok=True)
            union_json_path = union_subdir / f"manifold_union_{model_id}.json"
            union_data = {
                "application": "manifold_extraction",
                "input": str(input_msh_path),
                "output": f"model_{model_id}_manifold_union_output.obj",
                "tag_label": "tag_0",
                "val_include": [
                    0.5,
                    1.1
                ],
                "manifold_union": True,
                "DEBUG_output": False
            }
            with open(union_json_path, "w") as f:
                json.dump(union_data, f, indent=4)

            subtract_subdir = subdir / f"manifold_subtract"
            subtract_subdir.mkdir(parents=True, exist_ok=True)
            subtract_json_path = subtract_subdir / f"manifold_subtract_{model_id}.json"
            subtract_data = {
                "application": "manifold_extraction",
                "input": str(input_msh_path),
                "output": f"model_{model_id}_manifold_subtract_output.obj",
                "tag_label": "tag_0",
                "val_include": [
                    0.5,
                    1.1
                ],
                "manifold_union": False,
                "DEBUG_output": False
            }
            with open(subtract_json_path, "w") as f:
                json.dump(subtract_data, f, indent=4)
            
            count += 2
    print(f"Created {count} jsons.")


if __name__ == "__main__":
    main()
