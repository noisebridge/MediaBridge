import os
import tarfile

import wget

"""
For our scripts to work, we need to download the Netflix prize data. As this file is ~500 MB and the licensing terms are dubious, 
we decided early on not to include it as part of the repo. It is however available on the Internet Archive here: 
https://archive.org/details/nf_prize_dataset.tar
"""


def download_file(url, output_path):
    os.makedirs(
        os.path.dirname(output_path), exist_ok=True
    )  # create directory if not already existing

    if os.path.exists(output_path):
        print(f"\nFile already exists: {output_path}")
        return None
    else:
        filename = wget.download(url, out=output_path)
        return filename


def extract_file(compressed_file_path, extract_to_path, check_file_path):
    if os.path.exists(check_file_path):
        print(f"\nFile '{check_file_path}' already exists. Skipping extraction.")
    else:
        print("\nExtracting...")
        with tarfile.open(compressed_file_path, "r:gz") as tar:
            tar.extractall(path=extract_to_path)


def move_files(source_path, destination_path):
    if not os.path.exists(source_path):
        print("\nSource file does not exist. Nothing to move")
    elif os.path.exists(destination_path):
        print(f"\nFile already exists: {destination_path}")
    else:
        os.rename(source_path, destination_path)
        print(f"\nMoving {source_path} to {destination_path}...")
        print("\nDownload Complete!")


def main():
    url = "https://archive.org/download/nf_prize_dataset.tar/nf_prize_dataset.tar.gz"
    compressed_filename = "nf_prize_dataset.tar.gz"
    data_dir = os.path.join(os.path.dirname(__file__), "../../data")
    download_dir = os.path.join(data_dir, "download")
    compressed_file_path = os.path.join(data_dir, compressed_filename)
    movie_titles_path = os.path.join(data_dir, "movie_titles.txt")
    file_name = "movie_titles.txt"
    source_path = os.path.join(download_dir, file_name)
    destination_path = os.path.join(data_dir, file_name)

    download_file(url, compressed_file_path)
    extract_file(compressed_file_path, data_dir, movie_titles_path)
    move_files(source_path, destination_path)


if __name__ == "__main__":
    main()
