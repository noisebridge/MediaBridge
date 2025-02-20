from pathlib import Path

if __package__ != "mediabridge":
    raise Exception(
        "File path definitions are incorrect, definitions.py is not in the root 'mediabridge' module."
    )

MODULE_DIR = Path(__file__).parent
PROJECT_DIR = MODULE_DIR.parent

DATA_DIR = PROJECT_DIR / "data"
NETFLIX_DATA_DIR = DATA_DIR / "nf_prize_dataset"
FULL_TITLES_TXT = NETFLIX_DATA_DIR / "movie_titles.txt"

OUTPUT_DIR = PROJECT_DIR / "out"
LIGHTFM_MODEL_PKL = OUTPUT_DIR / "lightfm_model.pkl"


if __name__ == "__main__":
    print(MODULE_DIR)
    print(PROJECT_DIR)
    print(DATA_DIR)
    print(OUTPUT_DIR)
