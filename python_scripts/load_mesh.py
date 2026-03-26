import thingi10k
import argparse
from pathlib import Path
from alive_progress import alive_bar
import os.path


def save_as_obj(verts, faces, out_path):
    with open(out_path, "w") as outf:
        for v in verts:
            outf.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for f in faces:
            outf.write(f"f {f[0]+1} {f[1]+1} {f[2]+1}\n")


def download_objs(cache_dir, out_dir):
    # init thingi10k cache
    thingi10k.init(cache_dir=cache_dir)
    out_dir_path = Path(out_dir)
    entries = list(thingi10k.dataset())
    with alive_bar(len(entries)) as bar:
        for i, entry in enumerate(entries):
            file_id = entry["file_id"]
            bar.text(f"Processing model {file_id}")
            try:
                verts, faces = thingi10k.load_file(entry["file_path"])
                out_subdir = out_dir_path / f"model_{file_id}"
                out_subdir.mkdir(parents=False, exist_ok=True)
                out_obj_path = out_subdir / f"model_{file_id}.obj"
                save_as_obj(verts, faces, str(out_obj_path))
                bar()
            except Exception as e:
                print(f"[{i+1}] Failed to load or save model {file_id}: {e}")
                bar()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download thingi10k and convert to .obj files")
    parser.add_argument("-c", "--cachedir", required=True, help="Directory to store raw .npz model files")
    parser.add_argument("-o", "--outdir", required=True, help="Directory to create subdir for each model to store .objs")
    args = parser.parse_args()
    download_objs(args.cachedir, args.outdir)
