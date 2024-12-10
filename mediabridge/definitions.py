from pathlib import Path

if __package__ != "mediabridge":
    raise Exception(
        "File path definitions are incorrect, definitions.py is not in the root 'mediabridge' module."
    )

MODULE_DIR = Path(__file__).parent
PROJECT_DIR = MODULE_DIR.parent
DATA_DIR = PROJECT_DIR.joinpath("data")
OUTPUT_DIR = PROJECT_DIR.joinpath("out")

if __name__ == "__main__":
    print(MODULE_DIR)
    print(PROJECT_DIR)
    print(DATA_DIR)
    print(OUTPUT_DIR)
