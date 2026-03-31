import argparse
from pathlib import Path


def check_subdirs(mesh_dir):
    print("Scanning subdirectories...")
    mesh_dir_path = Path(mesh_dir)
    counts = {"total": 0, "completed": 0}
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
            msh_path = twild_out_path / f"model_{model_id}_tetwild_output.msh"
            if msh_path.exists():
                counts["completed"] += 1
    print(f"{counts['completed']} / {counts['total']} completed ({counts['total'] - counts['completed']} remaining)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count existence of proper .msh files")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    args = parser.parse_args()
    check_subdirs(args.meshdir)