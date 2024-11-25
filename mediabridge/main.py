import logging
from contextlib import nullcontext
from datetime import datetime

import typer as typer
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.data_processing import wiki_to_netflix
from mediabridge.definitions import OUTPUT_DIR


def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
    log: bool = typer.Option(
        False, "--log", "-l", help="Enable all logging message levels and log to file."
    ),
    full: bool = typer.Option(
        False, "--full", "-f", help="Run processing on full dataset."
    ),
):
    if not OUTPUT_DIR.exists():
        print(
            f"[WARNING] Output directory does not exist, creating new directory at {OUTPUT_DIR}"
        )
        OUTPUT_DIR.mkdir()

    if log:
        # log all messages to new file
        logging.basicConfig(
            level=logging.DEBUG,
            filename=OUTPUT_DIR.joinpath(
                f"mb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            ),
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

    # We redirect logs to stdout through tqdm to avoid breaking progress bar.
    # But when logging to file, we use nullcontext or tqdm will redirect logs
    # back to stdout.
    with logging_redirect_tqdm() if not log else nullcontext():
        try:
            wiki_to_netflix.process_data(not full)
        except Exception as e:
            # include fatal exceptions with traceback in logs
            if log:
                logging.exception("Uncaught exception")
            raise e


if __name__ == "__main__":
    typer.run(main)
