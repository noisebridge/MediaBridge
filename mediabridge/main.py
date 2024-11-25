import logging
from datetime import datetime
from time import sleep

import typer as typer
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.data_processing import wiki_to_netflix
from mediabridge.definitions import OUTPUT_DIR


def main(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    log: bool = False,
    test: bool = False,
):
    # create output directory if it doesn't exist
    if not OUTPUT_DIR.exists():
        print(
            f"[WARNING] Output directory does not exist, creating new directory at {OUTPUT_DIR}"
        )
        OUTPUT_DIR.mkdir()

    if log:
        # log all messages to file
        logging.basicConfig(
            level=logging.DEBUG,
            filename=OUTPUT_DIR.joinpath(
                f"mb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            ),
            filemode="w",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        if verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")

    # Redirect logging to tqdm.write function to avoid colliding with
    # progress bar formatting
    with logging_redirect_tqdm():
        try:
            wiki_to_netflix.process_data(test)
        except Exception as e:
            # include fatal exceptions with traceback in log
            if log:
                logging.exception("Uncaught exception")
            raise e


if __name__ == "__main__":
    typer.run(main)
