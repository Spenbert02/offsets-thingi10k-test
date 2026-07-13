from pathlib import Path
import json

msh_dir_path = Path("/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes")
subdir = "wmtk_tetwild_test"
def model_name(model_id_):
    return f"model_{model_id_}_out_final.msh"
def report_name(model_id_):
    return f"model_{model_id_}_out_report.json"

def main():
    results = dict()
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

        out_msh_path = model_dir / subdir / model_name(model_id)
        if out_msh_path.exists():
            results_json_path = Path(model_dir / subdir / report_name(model_id))
            with open(results_json_path, "r") as f:
                json_dict = json.load(f)
                res_dict = dict()
                for key in ("time", "max_energy"):
                    res_dict[key] = json_dict[key]
                results[model_id] = res_dict
    
    print(results)

    # print results
    for model_id, res_dict in results:
        print(f"model {model_id}:")
        for key, val in res_dict:
            print(f"\t{key}: {val}")

if __name__ == "__main__":
    main()
