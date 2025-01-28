import csv
import dataclasses
import logging

from typer import Typer

from mediabridge.definitions import OUTPUT_DIR
from mediabridge.schemas.movies import EnrichedMovieData

log = logging.getLogger(__name__)
app = Typer()


@app.command()
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


if __name__ == "__main__":
    app()
