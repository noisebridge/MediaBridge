import logging
import shutil
import tarfile
from pathlib import Path

import requests
from tqdm import tqdm

from mediabridge.definitions import DATA_DIR, NETFLIX_DATA_DIR, OUTPUT_DIR

"""
For our scripts to work, we need to download the Netflix prize data. As this file is ~500 MB and the licensing terms are dubious, 
we decided early on not to include it as part of the repo. It is however available on the Internet Archive here: 
https://archive.org/details/nf_prize_dataset.tar
"""

log = logging.getLogger(__name__)


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        if content_length := r.headers.get("content-length"):
            total_length = int(content_length)
        for chunk in tqdm(
            r.iter_content(chunk_size=1024), total=(total_length // 1024) + 1
        ):
            if chunk:
                f.write(chunk)
                f.flush()


def extract_file(src: Path, dest: Path, gz_compressed: bool = False) -> None:
    print("\nExtracting...")
    mode = "r:gz" if gz_compressed else "r:"
    with tarfile.open(name=src, mode=mode) as tar:
        tar.extractall(path=dest)


def download_netflix_dataset() -> None:
    NETFLIX_DATA_DIR.mkdir(parents=True)
    url = "https://archive.org/download/nf_prize_dataset.tar/nf_prize_dataset.tar.gz"
    compressed_filename = "nf_prize_dataset.tar.gz"
    compressed_file_path = DATA_DIR / compressed_filename

    download_file(url, compressed_file_path)
    extract_file(compressed_file_path, DATA_DIR, gz_compressed=True)
    compressed_file_path.unlink()
    (DATA_DIR / "download").rename(DATA_DIR / "nf_prize_dataset")
    extract_file(
        NETFLIX_DATA_DIR / "training_set.tar", NETFLIX_DATA_DIR / "training_set"
    )
    (NETFLIX_DATA_DIR / "training_set.tar").unlink()


def clean_all() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
