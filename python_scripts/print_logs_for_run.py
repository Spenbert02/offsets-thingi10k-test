from pathlib import Path
import sys


logs_dir = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/offsets_array/logs"
MODEL_ID = 100331
SINGLEBODY = True


def main():
    logs_dir_path = Path(logs_dir)
    jobs = []
    for p in logs_dir_path.iterdir():
        if not (p.is_file() and p.suffix.lower() == ".out"):
            continue
        
        with open(str(p), "r") as f:
            f.readline()
            f.readline()
            name = Path(f.readline().split(" ")[2]).name.split("_")
            model_id = int(name[1])
            body = name[0]
            if model_id == MODEL_ID and ((body == "singlebody") if SINGLEBODY else (body == "twobody")):
                print(p.name)
                jobs.append([p.name.split("_")[1:3]])
    print(f"Found logs: ",end="")
    print([f"{ids[0]}_{ids[1]}" for ids in jobs])
    for job in jobs:
        out_path = logs_dir_path / f"job_{job[0]}_{job[1]}.out"
        print("========================")
        print(str(out_path))
        print("========================")
        with open(str(out_path), "r") as f:
            for line in f.readlines():
                print(line)
        print()
        err_path = logs_dir_path / f"job_{job[0]}_{job[1]}.err"
        print("========================")
        print(str(err_path))
        print("========================")
        with open(str(err_path), "r") as f:
            for line in f.readlines():
                print(line)


if __name__ == "__main__":
    main()