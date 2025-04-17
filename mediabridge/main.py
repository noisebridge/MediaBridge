import logging
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
import typer as typer

from mediabridge.data_download import clean_all, download_file, download_netflix_dataset
from mediabridge.data_processing import etl, wiki_to_netflix
from mediabridge.data_processing.etl import etl_movie_title
from mediabridge.db.load import load_from_sql
from mediabridge.db.tables import create_tables
from mediabridge.definitions import (
    DATA_DIR,
    LOGGING_DIR,
    NETFLIX_DATA_DIR,
    OUTPUT_DIR,
    PROJECT_DIR,
)
from mediabridge.integrations.ollama_api import generate_prompt_response
from mediabridge.recommender import make_recommendation
from mediabridge.recommender.tf_idf import (
    create_dataframe,
    recommend_multiple_items,
    transform,
)

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
            "[WARNING] Output directory does not exist, "
            f"creating new directory at {OUTPUT_DIR}"
        )
        OUTPUT_DIR.mkdir()

    if log:
        # log all messages to new file
        LOGGING_DIR.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            filename=LOGGING_DIR / f"mb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
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
def init(
    refresh: bool = typer.Option(
        False, help="Deletes data-holding directories before initializing."
    ),
) -> None:
    """Download all required datasets and initialize the database"""
    if refresh:
        clean_all()

    if NETFLIX_DATA_DIR.exists():
        logging.error(
            f"The Netflix Prize dataset already exists in {NETFLIX_DATA_DIR.relative_to(PROJECT_DIR)}. "
            "Please use the --refresh option if you intend to initialize from scratch.",
        )
        return

    download_netflix_dataset()
    create_tables()


@app.command()
def load(max_reviews: int = 101_000_000, regen: bool = False) -> None:
    """Load all dataset data into the databases for processing"""
    if regen:
        prompt = "\n! Are you sure you want to delete ALL existing sqlite data? y/n !\n"
        if input(prompt) != "y":
            print("\nAborting process.")
            return
    etl.etl(max_reviews=max_reviews, regen=regen)


@app.command()
def load_mongo(regen: bool = False) -> None:
    """Load data from SQLite into MongoDB"""
    if regen:
        prompt = "\n! Are you sure you want to delete all MongoDB data in the movies collection? y/n !\n"
        if input(prompt) != "y":
            print("\nAborting process.")
            return
    etl_movie_title()
    load_from_sql(regen=regen)


@app.command()
def tf_idf(
    movies: list[str] = typer.Argument(..., help="Movie titles to analyze"),
    alpha: float = typer.Option(0.5),
    beta: float = typer.Option(0.7),
    gamma: float = typer.Option(2.0),
    top_k: int = typer.Option(5),
):
    url = "http://ollama.tomato-pepper.uk/movie_titles_plus_descriptions.jsonl"
    raw_data_path = DATA_DIR / "movie_titles_plus_descriptions.jsonl"
    df_path = DATA_DIR / "tf_idf_dataframe.csv"
    sim_matrix_path = DATA_DIR / "cosine_similarity.npy"

    if not raw_data_path.exists():
        typer.echo("Downloading movie descriptions...")
        download_file(
            url,
            raw_data_path,
        )

    if df_path.exists():
        df = pd.read_csv(df_path)
    else:
        typer.echo("Creating DataFrame from raw data...")
        df = create_dataframe()
        df.to_csv(df_path, index=False)

    if sim_matrix_path.exists():
        similarity_matrix = np.load(sim_matrix_path)
    else:
        typer.echo("Computing cosine similarity matrix...")
        similarity_matrix = transform(df)
        np.save(sim_matrix_path, similarity_matrix)

    missing = [title for title in movies if title not in df["title"].values]
    if missing:
        typer.echo(f"Movie(s) not found: {', '.join(missing)}")
        raise typer.Exit(code=1)

    recommendations = recommend_multiple_items(
        titles=movies,
        data=df,
        similarity_matrix=similarity_matrix,
        top_k=top_k,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
    )

    typer.echo(f"Recommendations for {movies} ")
    typer.echo(recommendations.to_string(index=False))


@app.command()
def chat(
    prompt: str = typer.Argument(..., help="The prompt to send to the Ollama API."),
    model: str = typer.Option(
        "llama3", "--model", "-m", help="The model to use for generating the response."
    ),
) -> None:
    """Chat with the Ollama API."""
    typer.echo(f"Generating response to '{prompt}' using model '{model}'...")
    try:
        response = generate_prompt_response(model=model, prompt=prompt)
        typer.echo("\nResponse:")
        typer.echo(response)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    app()
