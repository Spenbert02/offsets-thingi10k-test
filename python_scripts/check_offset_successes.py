from pathlib import Path


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"


def main():
    mesh_dir_path = Path(mesh_dir)
    counts = {"success":0, "total":0}
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        counts["total"] += 2

        single_out_path = subdir / "singlebody" / f"model_{model_id}_singlebody_offset_output.msh"
        if single_out_path.exists():
            counts["success"] += 1
        
        twobody_out_path = subdir / "twobody" / f"model_{model_id}_twobody_offset_output.msh"
        if twobody_out_path.exists():
            counts['success'] += 1
    
    print(f"Offsets progress: {counts['success']} / {counts['total']} successes")


if __name__ == "__main__":
    main()