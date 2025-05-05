import csv
import dataclasses
import logging

from pymongo import InsertOne
from sqlalchemy import text
from typer import Typer

from mediabridge.db.connect import connect_to_mongo
from mediabridge.db.tables import get_engine
from mediabridge.definitions import OUTPUT_DIR
from mediabridge.schemas.movies import EnrichedMovieData

log = logging.getLogger(__name__)
app = Typer()


def load() -> None:
    """
    Load a csv of movie data into the mongo database.
    """
    with open(OUTPUT_DIR / "matches.csv", "r") as f:
        reader = csv.reader(f)

        header = next(reader)
        if header != [f.name for f in dataclasses.fields(EnrichedMovieData)]:
            raise ValueError(
                "Header does not match expected dataclass fields (EnrichedMovieData), "
                f"expected {dataclasses.fields(EnrichedMovieData)}, got {header}"
            )

        for row in reader:
            netflix_id, title, year, wikidata_id, genres, director = row
            movie = EnrichedMovieData(
                netflix_id,
                title,
                int(year),
                wikidata_id,
                genres.split(";"),
                director,
            )
            log.info(f"Inserting {movie} into MongoDB")
            # TODO: Needs implementation, bulk inserts for performance


def _make_movie_dict(movie: list[str]) -> dict[str, str]:
    return {
        "netflix_id": movie[0],
        "title": movie[1],
        "year": movie[2],
    }


def load_from_sql(regen: bool) -> None:
    """Load movies into the movies collection based on data in the sqlite database.

    Args:
        regen (bool): If True, the movies collection will be dropped and recreated.
    """
    mongo_movies = connect_to_mongo().movies
    if regen:
        mongo_movies.delete_many({})
    with get_engine().connect() as conn:
        operations = [
            InsertOne(_make_movie_dict(movie))
            for movie in conn.execute(text("SELECT id, title, year FROM movie_title"))
        ]
        mongo_movies.bulk_write(operations)


if __name__ == "__main__":
    app()
