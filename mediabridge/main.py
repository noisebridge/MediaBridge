import logging

import typer as typer
from tqdm import trange
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.data_processing import wiki_to_netflix

LOG = logging.getLogger(__name__)


def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    if verbose:
        logging.basicConfig(level=logging.INFO)

    # Redirect logging to tqdm.write function to avoid colliding with
    # progress bar formatting
    with logging_redirect_tqdm():
        for i in trange(9):
            if i == 4:
                LOG.info("console logging redirected to `tqdm.write()`")

    q = wiki_to_netflix.format_sparql_query("The Room", 2003)
    print(q)


if __name__ == "__main__":
    typer.run(main)
