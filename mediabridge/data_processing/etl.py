import re

import pandas as pd
from sqlalchemy.sql import text
from tqdm import tqdm

from mediabridge.data_processing.etl_helpers import (
    RATING_CSV,
    _insert_ratings,
    _read_ratings,
)
from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.tables import get_engine
from mediabridge.definitions import FULL_TITLES_TXT, PROJECT_DIR

GLOB = "mv_00*.txt"


def etl(max_rows: int) -> None:
    """Extracts, transforms, and loads ratings data into a combined uniform CSV + rating table.

    If CSV or table have already been computed, we skip repeating that work to save time.
    It is always safe to force a re-run with:
    $ (cd out && rm -f rating.csv movies.sqlite)
    """
    _etl_movie_title()
    _etl_user_rating(max_rows)


def _etl_movie_title() -> None:
    query = "SELECT *  FROM movie_title  LIMIT 1"
    if pd.read_sql_query(query, get_engine()).empty:
        columns = ["id", "year", "title"]
        df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=columns)
        df["year"] = df.year.replace("NULL", pd.NA).astype("Int16")
        # At this point there's a df.id value of "1". Maybe it should be "00001"?

        with get_engine().connect() as conn:
            conn.execute(text("DELETE FROM rating"))
            conn.execute(text("DELETE FROM movie_title"))
            conn.commit()
            df.to_sql("movie_title", conn, index=False, if_exists="append")


def _etl_user_rating(max_rows: int) -> None:
    """Writes out/rating.csv if needed, then populates rating table from it."""
    training_folder = PROJECT_DIR.parent / "Netflix-Dataset/training_set/training_set"
    diagnostic = "Please clone  https://github.com/deesethu/Netflix-Dataset.git"
    assert training_folder.exists(), diagnostic
    path_re = re.compile(r"/mv_(\d{7}).txt$")
    is_initial = True
    if not RATING_CSV.exists():
        # Transform to "tidy" data, per Hadley Wickham, with a uniform "movie_id" column.
        with open(RATING_CSV, "w") as fout:
            for mv_ratings_file in tqdm(
                sorted(training_folder.glob(GLOB)), smoothing=0.01
            ):
                m = path_re.search(f"{mv_ratings_file}")
                assert m
                movie_id = int(m.group(1))
                df = pd.DataFrame(_read_ratings(mv_ratings_file, movie_id))
                assert not df.empty
                df["movie_id"] = movie_id
                df.to_csv(fout, index=False, header=is_initial)
                is_initial = False

    query = "SELECT *  FROM rating  LIMIT 1"
    if pd.read_sql_query(query, get_engine()).empty:
        _insert_ratings(RATING_CSV, max_rows)
