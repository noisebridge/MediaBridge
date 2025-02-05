"""
Recommends movies based on sparse input: the "cold start" problem.
"""

import io
import re
from collections.abc import Generator
from pathlib import Path
from subprocess import PIPE, Popen
from time import time

import pandas as pd
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.sql import text
from tqdm import tqdm

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.tables import RatingTemp, get_engine
from mediabridge.definitions import FULL_TITLES_TXT, PROJECT_DIR


def etl(glob: str) -> None:
    _etl_movie_title()
    _etl_user_rating(glob)


def _etl_movie_title() -> None:
    columns = ["id", "year", "title"]
    df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=columns)
    df["year"] = df.year.replace("NULL", pd.NA).astype("Int16")
    print(df)

    with get_engine().connect() as connection:
        connection.execute(text("DELETE FROM rating"))
        connection.execute(text("DELETE FROM rating_temp"))
        connection.execute(text("DELETE FROM movie_title"))
        connection.execute(text("COMMIT"))
        df.to_sql("movie_title", connection, index=False, if_exists="append")


def _etl_user_rating(glob: str) -> None:
    training_folder = PROJECT_DIR.parent / "Netflix-Dataset/training_set/training_set"
    diagnostic = "Please clone  https://github.com/deesethu/Netflix-Dataset.git"
    assert training_folder.exists(), diagnostic
    path_re = re.compile(r"/mv_(\d{7}).txt$")
    is_initial = True
    out_csv = Path("/tmp") / "rating.csv.gz"
    if not out_csv.exists():
        with open(out_csv, "wb") as fout:
            # We don't _need_ a separate gzip child process.
            # Specifying .to_csv('foo.csz.gz') would suffice.
            # But then we burn a single core while holding the GIL.
            # Forking a child lets use burn a pair of cores.
            gzip_proc = Popen(["gzip", "-c"], stdin=PIPE, stdout=fout)
            for file_path in tqdm(sorted(training_folder.glob(glob)), smoothing=0.01):
                m = path_re.search(f"{file_path}")
                assert m
                movie_id = int(m.group(1))
                df = pd.DataFrame(_read_ratings(file_path, movie_id))
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

    _insert_ratings(out_csv)


def _insert_ratings(csv: Path) -> None:
    with get_engine().connect() as conn:
        df = pd.read_csv(csv)
        conn.execute(text("DELETE FROM rating_temp"))
        conn.commit()
        print(".")
        rows = [
            {str(k): int(v) for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]
        print(".")
        with Session(conn) as sess:
            t0 = time()
            sess.bulk_insert_mappings(class_mapper(RatingTemp), rows)
            sess.commit()
            print(f"wrote {len(rows)} rating_temp rows in {time()-t0:.3f} s")

            ins = """
            INSERT INTO rating (movie_id, user_id, rating)
            SELECT movie_id, user_id, rating
            FROM rating_temp
            ORDER BY movie_id, user_id
            """
            t0 = time()
            sess.execute(text(ins))
            sess.execute(text("DELETE FROM rating_temp"))
            sess.commit()
            print(f"wrote {len(rows)} rating rows in {time()-t0:.3f} s")


def _read_ratings(
    file_path: Path, movie_id: int
) -> Generator[dict[str, int], None, None]:
    with open(file_path, "r") as fin:
        line = fin.readline()
        assert line == f"{movie_id}:\n"
        for line in fin:
            user_id, rating, _ = line.strip().split(",")
            yield {
                "user_id": int(user_id),
                "rating": int(rating),
            }
