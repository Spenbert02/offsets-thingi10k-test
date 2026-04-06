from pathlib import Path


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"


def main():
    mesh_dir_path = Path(mesh_dir)
    id_str = ""
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        single_out_path = subdir / "singlebody" / f"model_{model_id}_singlebody_offset_output.msh"
        if not single_out_path.exists():
            id_str += f" {model_id}-single"
        
        twobody_out_path = subdir / "twobody" / f"model_{model_id}_twobody_offset_output.msh"
        if not twobody_out_path.exists():
            id_str += f" {model_id}-two"
    
    print(f"Failed models: {id_str}")


if __name__ == "__main__":
    main()