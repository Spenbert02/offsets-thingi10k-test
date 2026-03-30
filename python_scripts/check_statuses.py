import argparse
from pathlib import Path
import thingi10k


def scan_directories(log_fpath, cache_dir):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check which model(s) did not run.")
    parser.add_argument("-l", "--logfile", required=True, help="Path to log (.out) file")
    parser.add_argument("-c", "--cachedir", required=True, help="Path to cache dir for thingi10k")
    args = parser.parse_args()
    scan_directories(args.logfile, args.cachedir)