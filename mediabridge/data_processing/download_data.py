import tarfile
from pathlib import Path

import wget

"""
For our scripts to work, we need to download the Netflix prize data. As this file is ~500 MB and the licensing terms are dubious, 
we decided early on not to include it as part of the repo. It is however available on the Internet Archive here: 
https://archive.org/details/nf_prize_dataset.tar
"""


def download_file(url, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    filename = wget.download(url, out=str(output_path))
    return filename


def extract_file(compressed_file_path, extract_to_path):
    print("\nExtracting...")
    with tarfile.open(compressed_file_path, "r:gz") as tar:
        tar.extractall(path=extract_to_path)


def move_files(source_path, destination_path):
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.rename(destination_path)
    print(f"\nMoving {source_path} to {destination_path}...")
    print("\nDownload Complete!")


def download_prize_dataset():
    url = "https://archive.org/download/nf_prize_dataset.tar/nf_prize_dataset.tar.gz"
    compressed_filename = "nf_prize_dataset.tar.gz"
    data_dir = Path(__file__).resolve().parent.parent / "data"
    download_dir = data_dir / "download"
    compressed_file_path = data_dir / compressed_filename
    file_name = "movie_titles.txt"
    source_path = download_dir / file_name
    destination_path = data_dir / file_name

    download_file(url, compressed_file_path)
    extract_file(compressed_file_path, data_dir)
    move_files(source_path, destination_path)


if __name__ == "__main__":
    download_prize_dataset()
