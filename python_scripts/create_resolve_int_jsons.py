from pathlib import Path
import json
import random

msh_dir_path = Path("/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes")

def main():
    if not msh_dir_path.exists():
        raise FileNotFoundError(str(msh_dir_path))

    model_ids = []
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
                continue

            model_ids.append(model_id)
    
    # randomly shuffle (fixed seed)
    shuffled_ids = sorted(model_ids)
    random.seed(42)
    random.shuffle(shuffled_ids)
    if len(shuffled_ids) % 2 == 1:
        shuffled_ids = shuffled_ids[:-1]
    
    # create jsons
    created = 0
    for i in range(len(shuffled_ids) // 2):
        id1 = shuffled_ids[2*i]
        id2 = shuffled_ids[(2*i)+1]
        min_id = min(id1, id2)

        # remeshing stuff
        remeshing_json = {
            "application": "image_simulation",
            "input": [ str(msh_dir_path / f"model_{id1}" / f"model_{id1}.obj"),
                        str(msh_dir_path / f"model_{id2}" / f"model_{id2}.obj") ],
            "skip_simplify": False,
            "eps_simplify_rel": 1e-2,
            "eps_rel": 1e-2,
            "preserve_topology": False,
            "stop_energy": 100,
            "num_threads": 1,
            "output": f"pair_{i}_out",
            "w_amips": 1e-4
        }
        remesh_out_dir = msh_dir_path / f"model_{min_id}" / "pair_remesh_test1"
        remesh_out_dir.mkdir(parents=True, exist_ok=True)
        remesh_json_path = remesh_out_dir / f"pair_{i}_remesh.json"
        with open(remesh_json_path, "w") as f:
            json.dump(remeshing_json, f, indent=4)
        
        # resolve intersection
        resolve_json = {
            "application": "image_simulation",
            "operation": "resolve_intersections",
            "input": [ str(remesh_out_dir / f"pair_{i}_out.msh") ],
            "resolve_intersections_tags": [[0, 1]]
        }
        resolve_out_dir = msh_dir_path / f"model_{min_id}" / "pair_resolve_int_test1"
        resolve_out_dir.mkdir(parents=True, exist_ok=True)
        resolve_json_path = resolve_out_dir / f"pair_{i}_resolve_int.json"
        with open(resolve_json_path, "w") as f:
            json.dump(resolve_json, f, indent=4)

        created += 2
    print(f"{created} jsons created.")


if __name__ == "__main__":
    main()
