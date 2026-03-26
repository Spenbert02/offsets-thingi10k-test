import argparse
import time
import subprocess
from pathlib import Path
import concurrent.futures
import os


def process_single_mesh(tetwild_exe, input_path, output_path):
    start_time = time.time()
    command = [tetwild_exe, "--input", str(input_path), "--output", str(output_path), "--save-mid-result", "2"]
    result = subprocess.run(command, capture_output=True, text=True)

    # delete non .msh files in output
    if result.returncode == 0:
        out_dir = output_path.parent
        for p in out_dir.iterdir():
            if p.is_file():
                if p.suffix.lower() != ".msh":
                    p.unlink()
                else: # assumes one .msh file in directory
                    target = out_dir / f"{output_path.name}.msh"
                    p.rename(target)

    duration = time.time() - start_time
    return input_path, result.returncode, result.stderr, duration


def process_meshes(meshdir, tetwild_exe):
    meshdir_path = Path(meshdir)
    io_mesh_pairs = []
    for model_dir in meshdir_path.glob("model_*"):
        if not model_dir.is_dir():
            continue

        try:
            id = int(model_dir.name.split('_')[1])
        except ValueError:
            continue

        model_path = model_dir / f"model_{id}.obj"
        if model_path.exists():
            output_subdir = model_dir / f"tetwild_output"
            output_subdir.mkdir(parents=True, exist_ok=True)
            output_path = output_subdir / f"model_{id}_tetwild_output"
            io_mesh_pairs.append([model_path, output_path])
        else:
            print(f"Warning: model [{str(model_path)}] does not exist")
    print(f"Found {len(io_mesh_pairs)} total meshes to process")

    max_workers = os.cpu_count()
    total_jobs = len(io_mesh_pairs)
    counts = [0, 0, 0]
    glob_start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_mesh, tetwild_exe, pair[0], pair[1]) : pair[0]
            for pair in io_mesh_pairs
        }

        for future in concurrent.futures.as_completed(futures):
            input_path, returncode, stderr, duration = future.result()
            counts[2] += 1
            total_time = time.time() - glob_start_time
            time_stats = f"(took {duration:.2f}s | total elapsed: {total_time:.2f}s)"

            if returncode == 0:
                counts[0] += 1
                progress = f"[{counts[0] + counts[1]}/{total_jobs}] [{counts[0]} success|{counts[1]} fail]"
                print(f"{progress} [SUCCESS] {input_path.name} {time_stats}")
            else:
                counts[1] += 1
                progress = f"[{counts[0] + counts[1]}/{total_jobs}] [{counts[0]} success|{counts[1]} fail]"
                print(f"{progress} [FAILED] {input_path.name} (Return code: {returncode}) {time_stats}")
                print(f"\tError output: {stderr}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce .MSH objects for each .OBJ mesh using TetWild")
    parser.add_argument("-m", "--meshdir", required=True, help="Directory containing /model_i/ subdirectories")
    parser.add_argument("-e", "--tetwild", required=True, help="Path to build TetWild executable")
    args = parser.parse_args()
    process_meshes(args.meshdir, args.tetwild)
