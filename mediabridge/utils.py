import shutil
import tarfile
from pathlib import Path

import requests
from tqdm import tqdm

from mediabridge.definitions import DATA_DIR, OUTPUT_DIR

"""
For our scripts to work, we need to download the Netflix prize data. As this file is ~500 MB and the licensing terms are dubious, 
we decided early on not to include it as part of the repo. It is however available on the Internet Archive here: 
https://archive.org/details/nf_prize_dataset.tar
"""


def download_file(url: str, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        total_length = int(r.headers.get("content-length"))
        for chunk in tqdm(
            r.iter_content(chunk_size=1024), total=(total_length // 1024) + 1
        ):
            if chunk:
                f.write(chunk)
                f.flush()


def extract_file(file_path, extract_to_path, compression=""):
    print("\nExtracting...")
    with tarfile.open(file_path, f"r:{compression}") as tar:
        tar.extractall(path=extract_to_path)


def download_prize_dataset():
    url = "https://archive.org/download/nf_prize_dataset.tar/nf_prize_dataset.tar.gz"
    compressed_filename = "nf_prize_dataset.tar.gz"
    compressed_file_path = DATA_DIR / compressed_filename
    dataset_path = DATA_DIR / "nf_prize_dataset"

    download_file(url, compressed_file_path)
    extract_file(compressed_file_path, DATA_DIR, compression="gz")
    compressed_file_path.unlink()
    (DATA_DIR / "download").rename(DATA_DIR / "nf_prize_dataset")
    extract_file(dataset_path / "training_set.tar", dataset_path / "training_set")
    (dataset_path / "training_set.tar").unlink()


def clean_all():
    shutil.rmtree(DATA_DIR)
    shutil.rmtree(OUTPUT_DIR)
