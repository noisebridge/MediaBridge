import csv
import dataclasses
import logging

from typer import Typer

from mediabridge.definitions import OUTPUT_DIR
from mediabridge.schemas import EnrichedMovieData

log = logging.getLogger(__name__)
app = Typer()


@app.command()
def load():
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
            movie = EnrichedMovieData(*row)
            log.info(f"Inserting {movie} into MongoDB")
            # TODO: Needs implementation, bulk inserts for performance


if __name__ == "__main__":
    app()
