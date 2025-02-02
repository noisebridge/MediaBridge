"""
Recommends movies based on sparse input: the "cold start" problem.
"""

from collections.abc import Generator
from pathlib import Path

import pandas as pd
from sqlalchemy.sql import text

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.tables import get_engine
from mediabridge.definitions import FULL_TITLES_TXT, PROJECT_DIR


def etl() -> None:
    _etl_movie_title()
    _etl_user_rating()


def _etl_movie_title() -> None:
    columns = ["id", "year", "title"]
    df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=columns)
    df["year"] = df.year.replace("NULL", pd.NA).astype("Int16")
    print(df)

    with get_engine().connect() as connection:
        connection.execute(text("DELETE FROM movie_title"))
        df.to_sql("movie_title", connection, index=False, if_exists="append")


def _etl_user_rating(glob: str = "mv_000000*.txt") -> None:
    training_folder = PROJECT_DIR.parent / "Netflix-Dataset/training_set/training_set"
    diagnostic = "Please clone  https://github.com/deesethu/Netflix-Dataset.git"
    assert training_folder.exists(), diagnostic

    for file_path in sorted(training_folder.glob(glob)):
        print(file_path)
        df = pd.DataFrame(_read_ratings(file_path))
        print(df.tail(2))


def _read_ratings(file_path: Path) -> Generator[dict[str, int], None, None]:
    with open(file_path, "r") as fin:
        #     movie_id = int(fin.readline().rstrip().rstrip(":"))
        fin.readline()
        for line in fin:
            user_id, rating, _ = line.strip().split(",")
            yield {
                "user_id": int(user_id),
                "rating": int(rating),
            }
