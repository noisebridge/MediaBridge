import io
import logging
import re
from collections.abc import Generator
from pathlib import Path
from subprocess import PIPE, Popen
from time import time

import pandas as pd
import typer
from sqlalchemy import inspect
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.sql import text
from tqdm import tqdm

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.tables import (
    POPULAR_MOVIE_QUERY,
    PROLIFIC_USER_QUERY,
    Rating,
    create_tables,
    get_engine,
)
from mediabridge.definitions import DATA_DIR, FULL_TITLES_TXT, OUTPUT_DIR

app = typer.Typer()
log = logging.getLogger(__name__)

GLOB = "mv_00*.txt"


@app.command()
def etl(regen: bool = False, max_reviews: int = 100_000_000) -> None:
    """Extracts, transforms, and loads ratings data into a combined uniform CSV + rating table.

    If CSV or table have already been computed, we skip repeating that work to save time.
    It is always safe to force a re-run with:
    $ (cd out && rm -f rating.csv.gz movies.sqlite)
    """
    engine = get_engine()

    if regen:
        prompt = "\n! Are you sure you want to delete ALL existing sqlite data? y/n !\n"
        if input(prompt) != "y":
            print("\nAborting process\n")
            return
        log.info("Dropping existing tables...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS rating"))
            conn.execute(text("DROP TABLE IF EXISTS movie_title"))
            conn.commit()
        create_tables()
        # Delete compressed csv?

    log.info("Loading movie info into db...")
    _etl_movie_title()
    _etl_user_rating(max_reviews)


def _etl_movie_title() -> None:
    insp = inspect(get_engine())
    if insp.has_table("movie_title"):
        query = "SELECT *  FROM movie_title  LIMIT 1"
        # if there is already data in movie_title, skip reprocessing
        if not pd.read_sql_query(query, get_engine()).empty:
            log.warning(
                "movie_title table already populated with data, skipping reprocessing..."
            )
            return

    columns = ["id", "year", "title"]
    df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=columns)
    df["year"] = df.year.replace("NULL", pd.NA).astype("Int16")
    # At this point there's a df.id value of "1". Maybe it should be "00001"?

    with get_engine().connect() as conn:
        df.to_sql("movie_title", conn, index=False, if_exists="append")


def _etl_user_rating(max_reviews: int) -> None:
    """Writes out/rating.csv.gz if needed, then populates rating table from it."""
    training_folder = DATA_DIR / "training_set"
    diagnostic = "Please run `pipenv run dev init` to download the necessary dataset"
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

    _insert_ratings(out_csv, max_reviews)


def _insert_ratings(csv: Path, max_rows: int) -> None:
    """Populates rating table from compressed CSV, if needed."""
    # query = "SELECT *  FROM rating  LIMIT 1"
    # if not pd.read_sql_query(query, get_engine()).empty:
    #     return
    with get_engine().connect() as conn:
        df = pd.read_csv(csv, nrows=max_rows)
        print(f"\n{len(df):_}", end="", flush=True)
        rows = [
            {str(k): int(v) for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]
        print(end=" rating rows ", flush=True)
        with Session(conn) as sess:
            t0 = time()
            sess.bulk_insert_mappings(class_mapper(Rating), rows)
            sess.commit()
            print(f"written in {time() - t0:.3f} s")

            _gen_reporting_tables()
            #
            # example elapsed times:
            # 5_000_000 rating rows written in 16.033 s
            # 10_000_000 rating rows written in 33.313 s
            #
            # 100_480_507 rating rows written in 936.827 s
            # ETL finished in 1031.222 s (completes in ~ twenty minutes)


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
