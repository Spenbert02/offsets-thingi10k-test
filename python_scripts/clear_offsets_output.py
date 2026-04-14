from pathlib import Path


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"


def main():
    mesh_dir_path = Path(mesh_dir)
    cleared_count = 0
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        single_out_dir = subdir / "singlebody"
        if single_out_dir.exists():
            single_cleared = False
            for p in single_out_dir.iterdir():
                if p.suffix.lower() != ".json":
                    p.unlink()
                    single_cleared = True
            if single_cleared:
                cleared_count += 1
        
        two_out_dir = subdir / "twobody"
        if two_out_dir.exists():
            two_cleared = False
            for p in two_out_dir.iterdir():
                if p.suffix.lower() != ".json":
                    p.unlink()
                    two_cleared = True
            if two_cleared:
                cleared_count += 1
    
    print(f"{cleared_count} offset outputs cleared.")


if __name__ == "__main__":
    main()