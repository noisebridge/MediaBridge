"""
ETL helper functions, which aren't needed when we re-run tests.

These functions assist with extract, transform, and load tasks.
Typically there are two cases, barring a "partially complete" test run.
1. ratings.csv & movies.sqlite do not exist, so we re-create them.
2. ETL ran fine last time, so there's nothing to do.

Sequestering the helpers in this module makes coverage stats
easier to interpret. In case 2, this module is not used at all,
so it does not show up in test coverage reporting output.
During a more time-intensive case 1 run, 100% of lines are exercised.
"""

import io
from collections.abc import Generator
from pathlib import Path
from subprocess import PIPE, Popen
from time import time

import pandas as pd
from sqlalchemy.sql import text

from mediabridge.db.tables import (
    DB_FILE,
    POPULAR_MOVIE_QUERY,
    PROLIFIC_USER_QUERY,
    get_engine,
)
from mediabridge.definitions import OUTPUT_DIR

RATING_CSV = OUTPUT_DIR / "rating.csv"  # uncompressed, to accommodate sqlite .import


def _insert_ratings(csv: Path, max_rows: int) -> None:
    """Populates rating table from compressed CSV, if needed."""
    create_rating_csv = """
        CREATE TABLE rating_csv (
            user_id   INTEGER  NOT NULL,
            rating    INTEGER  NOT NULL,
            movie_id  TEXT     NOT NULL)
    """
    ins = "INSERT INTO rating  SELECT user_id, movie_id, rating  FROM rating_csv  ORDER BY 1, 2, 3"
    with get_engine().connect() as conn:
        print(f"\n{max_rows:_}", end="", flush=True)
        t0 = time()
        conn.execute(text("DROP TABLE  IF EXISTS  rating_csv"))
        conn.execute(text(create_rating_csv))
        conn.commit()
        _run_sqlite_child(
            [
                ".mode csv",
                ".headers on",
                f".import {_get_input_csv(max_rows)} rating_csv",
            ]
        )
        print(end=" rating rows ", flush=True)
        conn.execute(text("DELETE FROM rating"))
        conn.execute(text(ins))
        conn.execute(text("DROP TABLE rating_csv"))
        conn.commit()
        conn.execute(text("VACUUM"))
        print(f"written in {time() - t0:.3f} s")

        _gen_reporting_tables()
        #
        # example elapsed times:
        # 10_000_000 rating rows written in 18.560 s
        #
        # 101_000_000 rating rows written in 225.923 s (four minutes)
        # ETL finished in 468.062 s (eight minutes)


def _get_input_csv(max_rows: int, all_rows: int = 100_480_507) -> Path:
    """Optionally subsets the input prize data, doing work only in the subset case."""
    csv = RATING_CSV
    if max_rows < all_rows:
        df = pd.read_csv(csv, nrows=max_rows)
        csv = OUTPUT_DIR / "rating-small.csv"
        df.to_csv(csv, index=False)
    assert csv.exists(), csv
    return Path(csv)


def _run_sqlite_child(cmds: list[str]) -> None:
    with Popen(
        ["sqlite3", DB_FILE],
        text=True,
        stdin=PIPE,
        stdout=PIPE,
    ) as proc:
        assert isinstance(proc.stdin, io.TextIOWrapper)
        for cmd in cmds:
            proc.stdin.write(f"{cmd}\n")


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
