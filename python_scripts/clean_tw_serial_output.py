import argparse
from pathlib import Path


def scan_dirs(meshes_dir):
    msh_dir_path = Path(meshes_dir)
    if not msh_dir_path.exists():
        raise FileNotFoundError(str(msh_dir_path))

    counts = {"good": 0, "unprocessed": 0, "cleaned": 0, "total": 0}
    for subdir in msh_dir_path.glob("model_*"):
        if subdir.exists() and subdir.is_dir():
            try:
                model_id = int(subdir.name.split("_")[1])
            except:
                print(f"WARNING: non int dir name: {subdir.name}")
                continue
            
            counts["total"] += 1
            
            twild_output_dir = subdir / "tetwild_output"
            if not (twild_output_dir.exists() and twild_output_dir.is_dir()):
                counts["unprocessed"] += 1
                continue

            output_msh_path = twild_output_dir / f"model_{model_id}_tetwild_output.msh"
            if output_msh_path.exists():
                counts["good"] += 1
                continue

            msh_files = list(twild_output_dir.glob("*.msh"))
            if len(msh_files) == 1:
                for p in twild_output_dir.iterdir():
                    if p.is_file():
                        if p.suffix.lower() == ".msh":
                            p.rename(output_msh_path)
                        else:
                            p.unlink()
                counts["cleaned"] += 1
            else:
                counts["unprocessed"] += 1
                continue
    print(f"{counts['cleaned']} / {counts['total']} directories cleaned ({counts['unprocessed']} unfinished, {counts['good']} already clean)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean tetwild output directories")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    args = parser.parse_args()
    scan_dirs(args.meshdir)
