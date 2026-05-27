from pathlib import Path

mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
REMESHING_TEST_NUM = 5

def main():
    mesh_dir_path = Path(mesh_dir)
    cleared_counts = [0, 0]
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        remeshing_outdir = subdir / f"remeshing_test{REMESHING_TEST_NUM}"
        if remeshing_outdir.exists():
            any_deleted = False
            for p in remeshing_outdir.iterdir():
                if p.suffix.lower() != ".json":
                    any_deleted = True
                    p.unlink()
                    cleared_counts[1] += 1
            if any_deleted:
                cleared_counts[0] += 1
    
    print(f"{cleared_counts[1]} files deleted (across {cleared_counts[0]} directories)")


if __name__ == "__main__":
    main()