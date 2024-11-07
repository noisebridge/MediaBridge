import logging

import typer as typer
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.data_processing import wiki_to_netflix

LOG = logging.getLogger(__name__)


def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    if verbose:
        logging.basicConfig(level=logging.INFO)

    # Redirect logging to tqdm.write function to avoid colliding with
    # progress bar formatting
    with logging_redirect_tqdm():
        wiki_to_netflix.process_data(True)


if __name__ == "__main__":
    typer.run(main)
