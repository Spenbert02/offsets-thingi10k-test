import argparse
from pathlib import Path


def check_subdirs(mesh_dir):
    print("Scanning subdirectories...")
    mesh_dir_path = Path(mesh_dir)
    counts = {"total": 0, "tw completed": 0, "renamed": 0, "retagged": 0, "unprocessed": 0}
    for subdir in mesh_dir_path.glob("model_*"):
        if not (subdir.exists() and subdir.is_dir()):
            continue

        try:
            model_id = int(subdir.name.split("_")[1])
        except:
            continue

        counts["total"] += 1

        twild_out_path = subdir / "tetwild_output"
        if twild_out_path.exists():
            retag_path = twild_out_path / f"model_{model_id}_tetwild_output_retagged.msh"
            if retag_path.exists():
                counts["retagged"] += 1
                continue
            renamed_path = twild_out_path / f"model_{model_id}_tetwild_output.msh"
            if renamed_path.exists():
                counts["renamed"] += 1
                continue
            twild_outfiles = list(twild_out_path.glob("*.msh"))
            if len(twild_outfiles) > 0:
                counts["tw completed"] += 1
            else:
                counts["unprocessed"] += 1
        else:
            counts["unprocessed"] += 1
    for key, val in counts.items():
        print(f"{key} : {val}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count existence of proper .msh files")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    args = parser.parse_args()
    check_subdirs(args.meshdir)