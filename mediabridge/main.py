import logging
from dataclasses import dataclass
from datetime import datetime

import typer as typer

from mediabridge.data_processing import wiki_to_netflix
from mediabridge.definitions import OUTPUT_DIR

app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(wiki_to_netflix.app)


@dataclass
class AppContext:
    log: bool = False


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging."
    ),
    log: bool = typer.Option(
        False, "--log", "-l", help="Enable all logging message levels and log to file."
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
    ctx.obj = AppContext(log=log)


if __name__ == "__main__":
    app()
