from pathlib import Path
import re

REMESHING_TEST_NUM = 5

msh_dir_path = Path("/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes")
logs_dir_path = Path(f"/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test{REMESHING_TEST_NUM}_array/logs")

def get_most_recent_log(model_id):
    ret_id = 0
    if not (logs_dir_path / f"model_{model_id}_(0).out").exists():
        return None
    else:
        while (logs_dir_path / f"model_{model_id}_({ret_id + 1}).out").exists():
            ret_id += 1
        return ret_id

def main():
    ids = {}
    ids["success"] = []
    ids["seg_fault"] = []
    ids["bad_energy"] = []
    ids["timeout"] = []
    ids["other"] = []
    ids["OOM"] = []
    ids["empty_input"] = []
    ids["not_run"] = []

    count = 0
    print(f"progress: {count}\t", end="")
    for model_dir in msh_dir_path.glob("model_*"):
        count += 1
        if count % 100 == 0:
            print(f"\rprogress: {count}\t", end="", flush=True)

        if not model_dir.is_dir():
            continue

        try:
            model_id = int(model_dir.name.split('_')[1])
        except ValueError:
            print(f"\nWARNING: non-int model id at {str(model_dir)}")
            continue
    
        out_msh_path = model_dir / f"remeshing_test{REMESHING_TEST_NUM}" / f"model_{model_id}_out.msh"
        if out_msh_path.exists():
            # load out file to check for final energy
            log_num = get_most_recent_log(model_id)
            if log_num is not None:
                out_path = logs_dir_path / f"model_{model_id}_({log_num}).out"
                with open(str(out_path), "r") as f:
                    lines = f.readlines()
                    energy_line = lines[-2]
                    match = re.search(r"final max energy = ([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)", energy_line)
                    if match:
                        final_energy = float(match.group(1))
                        if final_energy < 100.0:
                            ids["success"].append(model_id)
                            continue
                        else:
                            ids["bad_energy"].append(model_id)
                            continue

            # out_log_path = model_dir / f"remeshing_test{REMESHING_TEST_NUM}" / f"model_{model_id}_out.log"
            # if out_log_path.exists():
            #     with open(str(out_log_path), "r") as f:
            #         lines = f.readlines()
            #         energy = float(lines[2][12:])
            #         if energy < 100.0:
            #             ids["success"].append(model_id)
            #             continue
            #         else:
            #             ids["bad_energy"].append(model_id)
            #             continue
        
        # load err file to see what went wrong
        log_num = get_most_recent_log(model_id)
        if log_num is not None:
            err_path = logs_dir_path / f"model_{model_id}_({log_num}).err"
            with open(str(err_path), "r") as f:
                lines = f.readlines()
                found = False
                for line in lines:
                    if "Segmentation fault" in line:
                        ids["seg_fault"].append(model_id)
                        found = True
                        break
                    if "DUE TO TIME LIMIT" in line:
                        ids["timeout"].append(model_id)
                        found = True
                        break
                    if "OOM Killed" in line:
                        ids["OOM"].append(model_id)
                        found = True
                        break
                if found:
                    continue
        
            # load out file to check for empty input
            out_path = logs_dir_path / f"model_{model_id}_({log_num}).out"
            with open(str(out_path), "r") as f:
                lines = f.readlines()
                found = False
                for line in lines:
                    if ("[error]" in line) and ("Empty Input" in line):
                        ids["empty_input"].append(model_id)
                        found = True
                        break
                if found:
                    continue
            
            # case not caught.
            ids["other"].append(model_id)
        else:
            ids["not_run"].append(model_id)
    
    # print output
    print()
    print(f"======= Remeshing Test {REMESHING_TEST_NUM} Results ========")
    for key, lst in ids.items():
        if key == "other":
            continue
        print(key, ":", len(lst))
        if key in ["OOM"]:
            for id in ids[key]:
                print(f"\t{id},")
    print("other", ":", len(ids["other"]))
    print("\t", end="")
    for id in ids["other"]:
        print(f" {id},", end="")
    print()


if __name__ == "__main__":
    main()
