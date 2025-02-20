import logging
from dataclasses import dataclass
from datetime import datetime

import typer as typer

from mediabridge.data_download import (
    clean_all,
    download_prize_dataset,
)
from mediabridge.data_processing import etl, wiki_to_netflix
from mediabridge.definitions import DATA_DIR, NETFLIX_DATA_DIR, OUTPUT_DIR
from mediabridge.recommender import make_recommendation

app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(wiki_to_netflix.app)
app.add_typer(make_recommendation.app)


@dataclass
class AppContext:
    log_to_file: bool = False


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
    log: bool = typer.Option(
        False, "--log", "-l", help="Enable all logging message levels and log to file."
    ),
) -> None:
    if not OUTPUT_DIR.exists():
        print(
            f"[WARNING] Output directory does not exist, creating new directory at {OUTPUT_DIR}"
        )
        OUTPUT_DIR.mkdir()

    if log:
        # log all messages to new file
        logging.basicConfig(
            level=logging.DEBUG,
            filename=OUTPUT_DIR / f"mb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            filemode="x",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        if verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")
    ctx.obj = AppContext(log_to_file=log)


@app.command()
def init(force: bool = False) -> None:
    """Download all required datasets and initialize all data for recommendations"""
    if force or not NETFLIX_DATA_DIR.exists():
        download_prize_dataset()
    else:
        logging.info(f"{NETFLIX_DATA_DIR} already exists, skipping download...")


@app.command()
def clean() -> None:
    """Clean up all downloaded and generated data by removing the /data and /out directories."""
    prompt = f"\n! Are you sure you want to delete {DATA_DIR} and {OUTPUT_DIR}? y/n !\n"
    if input(prompt) != "y":
        print("\nAborting process.")
        return
    clean_all()


@app.command()
def load(max_reviews: int = 101_000_000, regen: bool = False) -> None:
    """Load all dataset data into the databases for processing"""
    if regen:
        prompt = "\n! Are you sure you want to delete ALL existing sqlite data? y/n !\n"
        if input(prompt) != "y":
            print("\nAborting process.")
            return
    etl.etl(max_reviews=max_reviews, regen=regen)


if __name__ == "__main__":
    app()
