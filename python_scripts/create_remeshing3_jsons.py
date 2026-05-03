from pathlib import Path
import json

msh_dir_path = Path("/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes")

def main():
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

            obj_path = subdir / f"model_{model_id}.obj"
            if not obj_path.exists():
                print(f"WARNING: obj for model {model_id} does not exist")

            output_dir = subdir / "remeshing_test3"
            output_dir.mkdir(parents=True, exist_ok=True)
            json_path = output_dir / f"remeshing_test3_{model_id}.json"
            json_data = {
                "application": "image_simulation",
                "input": [str(obj_path)],
                "skip_simplify": False,
                "eps_simplify_rel": 1e-2,
                "eps_rel": 1e-2,
                "preserve_topology": False,
                "stop_energy": 100,
                "num_threads": 1,
                "output": f"model_{model_id}_out",
                "w_amips": 1e-4
            }
            with open(json_path, "w") as f:
                json.dump(json_data, f, indent=4)

            count += 1
    print(f"Created {count} jsons.")


if __name__ == "__main__":
    main()
