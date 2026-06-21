from pathlib import Path
import subprocess

REMESHING_TEST_NUM = 6
CHUNK_SIZE = 1000
MAX_CHUNKS = None

# bad_energy = [
#     44111,
# 	58009
# ]
# timeout = [
#     1368052,
# 	252786,
# 	338910,
# 	46017,
# 	46024,
# 	55928
# ]
# oom = [
#     1313553,
# 	1619332,
# 	237741,
# 	41089,
# 	99468,
# 	99469,
# 	996816
# ]
# others = [
#     106830,
#     106838,
#     110904,
#     113906,
#     1313550,
#     138197,
#     1472696,
#     229959,
#     241232, 
#     241234, 
#     252784, 
#     282141, 
#     283361, 
#     286985, 
#     298323, 
#     325083, 
#     325161, 
#     325174, 
#     325191, 
#     325195, 
#     331745, 
#     331753, 
#     331802, 
#     331803, 
#     384574, 
#     41077, 
#     44057,
#     44739, 
#     47094, 
#     51454, 
#     51476,
#     51884, 
#     55134,
#     56105,
#     58939,
#     59340, 
#     611677, 
#     61393, 
#     61394, 
#     61764, 
#     63943, 
#     681062, 
#     688364, 
#     702413, 
#     73178, 
#     73446, 
#     76106, 
#     79787, 
#     80433, 
#     81262, 
#     81454, 
#     81568, 
#     82537, 
#     83597, 
#     84131, 
#     85111, 
#     90151, 
#     91945, 
#     940414, 
#     94240, 
#     94900, 
#     95985, 
#     97660, 
#     98571, 
#     99775
# ]

# bad_energy = []
# timeout = [
#     113906,
# 	1368052,
# 	252784,
# 	59340,
# 	73178,
# 	90151,
# 	940414
# ]
# oom = [
#     252786,
# 	338910,
# 	55928,
# 	996816
# ]
# others = []
# model_ids = bad_energy + timeout + oom + others

bad_energy = []
timeout = [
    1368052,
	252784,
	252786,
	338910,
	59340,
	73178,
	90151,
	940414
]
oom = [
    55928,
	996816
]
others = []
model_ids = bad_energy + timeout + oom + others

mesh_dir = f"/scratch/seb9449/offsets_testing_thingi10k/tagged_tet_mshes"
run_list_fpath = f"/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test{REMESHING_TEST_NUM}_array/pending_jobs.txt"
slurm_script_fpath = f"/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/remeshing_test{REMESHING_TEST_NUM}_array/remeshing_test{REMESHING_TEST_NUM}_submit_array.slurm"

def main():
    jsons_to_run = []
    for model_id in model_ids:
        json_path = Path(mesh_dir) / f"model_{model_id}" / f"remeshing_test{REMESHING_TEST_NUM}" / f"remeshing_test{REMESHING_TEST_NUM}_explicit_{model_id}.json"
        if not json_path.exists():
            print(f"WARNING: json {str(json_path)} does not exist")
        else:
            jsons_to_run.append(str(json_path))

    run_list_path = Path(run_list_fpath)
    
    num_jobs = len(jsons_to_run)
    print(f"Found {num_jobs} [remeshing_test{REMESHING_TEST_NUM}] jobs to run")
    chunks = [jsons_to_run[i:i + CHUNK_SIZE] for i in range(0, num_jobs, CHUNK_SIZE)]
    for idx, chunk in enumerate(chunks):
        if MAX_CHUNKS:
            if idx > (MAX_CHUNKS - 1):
                continue
        chunk_file = run_list_path.with_name(f"pending_jobs_{idx}.txt")
        with open(chunk_file, "w") as f:
            for json_path in chunk:
                f.write(f"{json_path}\n")
        arr_max = len(chunk) - 1
        slurm_script_path = Path(slurm_script_fpath)
        sbatch_cmd = ["sbatch", f"--array=0-{arr_max}", "--mail-user=seb9449@nyu.edu", "--mail-type=BEGIN,END,FAIL,REQUEUE", str(slurm_script_path), str(chunk_file)]
        print(f"Submitting chunk {idx+1}/{len(chunks)}: {' '.join(sbatch_cmd)}")
        try:
            subprocess.run(sbatch_cmd, check=True)
            print(f"Chunk {idx+1}/{len(chunks)} successfully committed to queue")
        except subprocess.CalledProcessError as e:
            print(f"Failed to submit chunk {idx}. Error: {e}")
            break
        except FileNotFoundError:
            print("Error: 'sbatch' command not found. Are you running this on the HPC login node?")
            break


if __name__ == "__main__":
    main()