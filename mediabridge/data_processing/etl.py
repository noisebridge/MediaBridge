import io
import re
from collections.abc import Generator
from pathlib import Path
from subprocess import PIPE, Popen
from time import time

import pandas as pd
from sqlalchemy.sql import text
from tqdm import tqdm

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.tables import (
    DB_FILE,
    POPULAR_MOVIE_QUERY,
    PROLIFIC_USER_QUERY,
    get_engine,
)
from mediabridge.definitions import FULL_TITLES_TXT, OUTPUT_DIR, PROJECT_DIR

GLOB = "mv_00*.txt"


def etl(max_rows: int) -> None:
    """Extracts, transforms, and loads ratings data into a combined uniform CSV + rating table.

    If CSV or table have already been computed, we skip repeating that work to save time.
    It is always safe to force a re-run with:
    $ (cd out && rm -f rating.csv.gz movies.sqlite)
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
    """Writes out/rating.csv.gz if needed, then populates rating table from it."""
    training_folder = PROJECT_DIR.parent / "Netflix-Dataset/training_set/training_set"
    diagnostic = "Please clone  https://github.com/deesethu/Netflix-Dataset.git"
    assert training_folder.exists(), diagnostic
    path_re = re.compile(r"/mv_(\d{7}).txt$")
    is_initial = True
    out_csv = OUTPUT_DIR / "rating.csv.gz"
    if not out_csv.exists():
        with open(out_csv, "wb") as fout:
            # We don't _need_ a separate gzip child process.
            # Specifying .to_csv('foo.csz.gz') would suffice.
            # But then we burn a single core while holding the GIL.
            # Forking a child lets use burn a pair of cores.
            gzip_proc = Popen(["gzip", "-c"], stdin=PIPE, stdout=fout)
            for mv_ratings_file in tqdm(
                sorted(training_folder.glob(GLOB)), smoothing=0.01
            ):
                m = path_re.search(f"{mv_ratings_file}")
                assert m
                movie_id = int(m.group(1))
                df = pd.DataFrame(_read_ratings(mv_ratings_file, movie_id))
                assert not df.empty
                df["movie_id"] = movie_id
                with io.BytesIO() as bytes_io:
                    df.to_csv(bytes_io, index=False, header=is_initial)
                    bytes_io.seek(0)
                    assert isinstance(gzip_proc.stdin, io.BufferedWriter)
                    gzip_proc.stdin.write(bytes_io.read())
                    is_initial = False

            assert isinstance(gzip_proc.stdin, io.BufferedWriter), gzip_proc.stdin
            gzip_proc.stdin.close()
            gzip_proc.wait()

    _insert_ratings(out_csv, max_rows)


def _insert_ratings(csv: Path, max_rows: int) -> None:
    """Populates rating table from compressed CSV, if needed."""
    create_rating_csv = """
        CREATE TABLE rating_csv (
            user_id   INTEGER  NOT NULL,
            rating    INTEGER  NOT NULL,
            movie_id  TEXT     NOT NULL)
    """
    ins = "INSERT INTO rating  SELECT user_id, movie_id, rating  FROM rating_csv  ORDER BY 1, 2, 3"
    cmds = [
        ".mode csv",
        ".headers on",
        f".import {_get_input_csv(max_rows)} rating_csv",
    ]
    query = "SELECT *  FROM rating  LIMIT 1"
    if pd.read_sql_query(query, get_engine()).empty:
        with get_engine().connect() as conn:
            print(f"\n{max_rows:_}", end="", flush=True)
            t0 = time()
            conn.execute(text("DROP TABLE  IF EXISTS  rating_csv"))
            conn.execute(text(create_rating_csv))
            conn.commit()
            with Popen(
                ["sqlite3", DB_FILE],
                text=True,
                stdin=PIPE,
                stdout=PIPE,
            ) as proc:
                print()
                for cmd in cmds:
                    proc.stdin.write(f"{cmd}\n")
            print(end=" rating rows ", flush=True)
            conn.execute(text("DELETE FROM rating"))
            conn.execute(text(ins))
            conn.execute(text("DROP TABLE rating_csv"))
            conn.commit()
            print(f"written in {time() - t0:.3f} s")

            _gen_reporting_tables()
            #
            # example elapsed times:
            # 10_000_000 rating rows written in 18.560 s
            #
            # 100_480_507 rating rows written in 936.827 s
            # ETL finished in 1031.222 s (completes in ~ twenty minutes)


def _get_input_csv(max_rows: int, all_rows: int = 100_480_507) -> Path:
    """Optionally subsets the input prize data, doing work only in the subset case."""
    csv = OUTPUT_DIR / "rating.csv"
    if max_rows < all_rows:
        df = pd.read_csv(csv, nrows=max_rows)
        csv = OUTPUT_DIR / "rating-small.csv"
        df.to_csv(csv, index=False)
    assert csv.exists(), csv
    return csv


def _read_ratings(
    mv_ratings_file: Path,
    movie_id: int,
) -> Generator[dict[str, int], None, None]:
    with open(mv_ratings_file, "r") as fin:
        line = fin.readline()
        assert line == f"{movie_id}:\n"
        for line in fin:
            user_id, rating, _ = line.strip().split(",")
            yield {
                "user_id": int(user_id),
                "rating": int(rating),
            }


def _gen_reporting_tables() -> None:
    """Generates a pair of reporting tables from scratch, discarding any old reporting rows."""
    RATING_V_DDL = """
    CREATE VIEW rating_v AS
    SELECT user_id, rating, mt.*
    FROM rating JOIN movie_title mt ON movie_id = mt.id
    """
    tbl_qry = [
        ("popular_movie", POPULAR_MOVIE_QUERY),
        ("prolific_user", PROLIFIC_USER_QUERY),
    ]
    with get_engine().connect() as conn:
        conn.execute(text("DROP VIEW  IF EXISTS  rating_v"))
        conn.execute(text(RATING_V_DDL))
        for table, query in tbl_qry:
            conn.execute(text(f"DELETE FROM {table}"))
            conn.execute(text(f"INSERT INTO {table}  {query}"))
            conn.commit()
