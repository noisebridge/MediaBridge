import logging
import os
import traceback
from datetime import datetime

import typer as typer
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.data_processing import wiki_to_netflix


def main(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    log: bool = False,
    test: bool = False,
):
    # create output directory if it doesn't exist
    if not os.path.exists("./out"):
        logging.warning(" /out directory does not exist, creating...")
        os.mkdir("./out")

    if log:
        # log all messages to file
        logging.basicConfig(
            level=logging.DEBUG,
            filename=f"out/mb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            filemode="w",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
        try:
            wiki_to_netflix.process_data(test)
        except Exception:
            # include fatal exceptions with traceback in log
            logging.exception("Uncaught exception")
        return

    if verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")

    # Redirect logging to tqdm.write function to avoid colliding with
    # progress bar formatting
    with logging_redirect_tqdm():
        wiki_to_netflix.process_data(test)


if __name__ == "__main__":
    typer.run(main)
