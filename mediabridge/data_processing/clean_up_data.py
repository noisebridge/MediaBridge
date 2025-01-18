import os
import shutil


def clean_data_folder(data_dir):
    """
    Deletes everything inside the 'data' folder but keeps the 'data' folder itself.
    """
    if not os.path.exists(data_dir):
        print(f"No 'data' folder found at {data_dir}. Nothing to clean.")
        return

    print(f"Cleaning up all contents of the 'data' folder at: {data_dir}...")

    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)

        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"Deleted file: {item_path}")
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"Deleted directory: {item_path}")

    print(f"All contents of the 'data' folder have been deleted.")


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "../../data")

    clean_data_folder(data_dir)


if __name__ == "__main__":
    main()
