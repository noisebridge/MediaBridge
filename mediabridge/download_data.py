import os
import tarfile

import wget

"""
For our scripts to work, we need to download the Netflix prize data. As this file is ~500 MB and the licensing terms are dubious, we decided early on not to include it as part of the repo. It is however available on the Internet Archive here: https://archive.org/details/nf_prize_dataset.tar

We should write a script that downloads this tarfile, decompresses it, and puts the contents in /data/.

Specifically, everything that is in the download directory that the tarfile produces should be in the /data/ directory. So if there is download/movie_titles.txt it should be /data/movie_titles.txt.

In general, this would be a good candidate for a bash script that does wget -> tar -xzf -> rename directory. But it would be better to do it in Python for portability reasons (some team members use Windows).

We can definitely download the file with requests, but it might not be the perfect fit. We should research if there is a wget type library for Python that we could use.

We can use the tarfile library to extract the files: https://docs.python.org/3/library/tarfile.html

Finally, renaming can be done with os or shutil: https://docs.python.org/3/library/os.html#os.rename
"""


def download_file(url, compressed_filename, data_dir):
    os.makedirs(data_dir, exist_ok=True)  # create directory if not already existing
    output_path = os.path.join(data_dir, compressed_filename)

    if os.path.exists(output_path):
        print(f"File already exists: {output_path}")
        return None
    else:
        filename = wget.download(url, out=output_path)
        return filename


def extract_file(compressed_filename, data_dir):
    compressed_file_path = os.path.join(data_dir, compressed_filename)

    if os.path.exists(download_dir):
        print(f"Directory '{download_dir}' already exists. Skipping extraction.")
    else:
        print("Extracting...")
        with tarfile.open(compressed_file_path, "r:gz") as tar:
            tar.extractall(path=data_dir, filter="data")


def move_files(data_dir, download_dir, filename):
    target_file = os.path.join(download_dir, filename)
    destination = os.path.join(data_dir, filename)

    if not os.path.exists(target_file):
        print("target file does not exist. Nothing to move")
    else:
        os.rename(target_file, destination)
        print(f"Moving {filename}...")
        print("Download Complete!")


if __name__ == "__main__":
    url = "https://archive.org/download/nf_prize_dataset.tar/nf_prize_dataset.tar.gz"
    compressed_filename = "nf_prize_dataset.tar.gz"
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    download_dir = os.path.join(data_dir, "download")
    file_name = "movie_titles.txt"

    download_file(url, compressed_filename, data_dir)
    extract_file(compressed_filename, data_dir)
    move_files(data_dir, download_dir, file_name)
