from pathlib import Path


mesh_dir = "/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"


def main():
    mesh_dir_path = Path(mesh_dir)
    cleared_counts = {"tw":0, "offsets":0}
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            print(f"WARNING: non-int model id at {str(subdir)}")
            continue

        twild_out_dir = subdir / "tetwild_output"
        if twild_out_dir.exists():
            twild_cleared = False
            for p in twild_out_dir.iterdir():
                p.unlink()
                twild_cleared = True
            if twild_cleared:
                cleared_counts["tw"] += 1

        single_out_dir = subdir / "singlebody"
        if single_out_dir.exists():
            single_cleared = False
            for p in single_out_dir.iterdir():
                if p.suffix.lower() != ".json":
                    p.unlink()
                    single_cleared = True
            if single_cleared:
                cleared_counts["offsets"] += 1
        
        two_out_dir = subdir / "twobody"
        if two_out_dir.exists():
            two_cleared = False
            for p in two_out_dir.iterdir():
                if p.suffix.lower() != ".json":
                    p.unlink()
                    two_cleared = True
            if two_cleared:
                cleared_counts["offsets"] += 1
    
    print(f"{cleared_counts['tw']} tetwild outputs and {cleared_counts['offsets']} offset outputs cleared.")


if __name__ == "__main__":
    main()