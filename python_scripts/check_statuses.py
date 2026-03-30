import argparse
from pathlib import Path
import thingi10k


def scan_directories(log_fpath, cache_dir, mesh_dir):
    # collect all model ids
    all_ids = set()
    thingi10k.init(cache_dir=cache_dir)
    for entry in thingi10k.dataset():
        all_ids.add(int(entry["file_id"]))

    # collect successes and failures
    success_ids = set()
    fail_ids = set()
    with open(log_fpath, "r") as log_file:
        for line in log_file:
            parts = line.split(" ")
            if parts[0][-5:] == "9995]":
                model_id = int(parts[5].split("_")[1].split(".")[0])
                if parts[4][1:-1] == "SUCCESS":
                    success_ids.add(model_id)
                elif parts[4][1:-1] == "FAILED":
                    fail_ids.add(model_id)
    
    # set stuff
    incomplete_ids = (all_ids - success_ids) - fail_ids
    print(f"total models: {len(all_ids)}")
    print(f"successes: {len(success_ids)}")
    print(f"failures: {len(fail_ids)}")
    print("incomplete ids:", end="")
    for inc_id in incomplete_ids:
        print(f" {inc_id}", end="")
    print()

    # scout file structure
    counts = {"total": 0, "complete": 0, "partial": 0, "non int id": 0, "multiple msh": 0, "no output": 0}
    mesh_dir_path = Path(mesh_dir)
    for subdir in mesh_dir_path.glob("model_*"):
        if subdir.is_dir():
            counts["total"] += 1
            try:
                model_id = int(subdir.name.split("_")[1])
            except:
                counts["non int id"] += 1
                continue

            twild_outdir = subdir / "tetwild_output"
            if not twild_outdir.exists():
                counts["no output"] += 1
                continue

            mshs = list(twild_outdir.glob("*.msh"))
            if len(mshs) > 1:
                counts["multiple msh"] += 1
                continue
            elif len(mshs) == 0:
                counts["no output"] += 1
            else:
                msh = mshs[0]
                if msh.name == f"model_{model_id}_tetwild_output.msh":
                    counts["complete"] += 1
                else:
                    counts["partial"] += 1
    print(f"{mesh_dir} statuses:")
    for key, value in counts.items():
        print(f"\t{key}: {value}")            


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check which model(s) did not run.")
    parser.add_argument("-l", "--logfile", required=True, help="Path to log (.out) file")
    parser.add_argument("-c", "--cachedir", required=True, help="Path to cache dir for thingi10k")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    args = parser.parse_args()
    scan_directories(args.logfile, args.cachedir, args.meshdir)