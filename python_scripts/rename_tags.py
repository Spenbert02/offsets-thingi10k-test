import argparse
from pathlib import Path


def scan_dirs(meshes_dir):
    msh_dir_path = Path(meshes_dir)
    if not msh_dir_path.exists():
        raise FileNotFoundError(str(msh_dir_path))

    counts = {"unprocessed": 0, "total": 0, "retagged": 0, "no in/out": 0, "already retagged": 0}
    no_in_out_ids = []
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

            retagged_msh_path = twild_output_dir / f"model_{model_id}_tetwild_output_retagged.msh"
            if retagged_msh_path.exists():
                counts["already retagged"] += 1
                continue

            input_msh_path = twild_output_dir / f"model_{model_id}_tetwild_output.msh"
            if not input_msh_path.exists():
                counts["unprocessed"] += 1
                continue

            with open(str(input_msh_path), "rb") as f:
                lines = f.readlines()
            modified = False
            for i, line in enumerate(lines):
                if b'in/out' in line:
                    lines[i] = line.replace(b'in/out', b'tag_0')
                    modified = True
                    break
            if modified:
                counts["retagged"] += 1
                with open(str(retagged_msh_path), "wb") as f:
                    f.writelines(lines)
            else:
                no_in_out_ids.append(model_id)
                counts["no in/out"] += 1
    print(f"{counts['retagged']} / {counts['total']} meshes retagged ({counts['unprocessed']} unprocessed, {counts['no in/out']} meshes missing in/out tag)")
    print("\tno in/out tag model ids:")
    for m_id in no_in_out_ids:
        print(f"\t\t{m_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create new .msh files with proper tag_0")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    args = parser.parse_args()
    scan_dirs(args.meshdir)
