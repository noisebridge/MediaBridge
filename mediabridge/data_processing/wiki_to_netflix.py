import csv
import dataclasses
import logging
import time
from contextlib import nullcontext
from pathlib import Path
from types import NoneType
from typing import Any, Iterator

import requests
import typer
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.definitions import FULL_TITLES_TXT, OUTPUT_DIR
from mediabridge.schemas.movies import EnrichedMovieData, MovieData

USER_AGENT = "Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>"
DEFAULT_TEST_ROWS = 100


class WikidataServiceTimeoutException(Exception):
    pass


app = typer.Typer()
log = logging.getLogger(__name__)


def read_netflix_txt(
    txt_file: Path,
    num_rows: int | None = None,
) -> Iterator[tuple[str, ...]]:
    """
    Reads rows from the Netflix dataset file.

    Parameters:
        txt_file: Path to the Netflix movie_titles.txt file.

        num_rows: Number of rows to read from the file, or if None,
        all rows are read.

    Yields:
        (id, year, title) tuples.
    """
    with open(txt_file, "r", encoding="ISO-8859-1") as netflix_data:
        for i, line in enumerate(netflix_data):
            if num_rows is not None and i >= num_rows:
                break
            yield tuple(line.rstrip().split(",", 2))


def create_netflix_csv(csv_path: Path, data_list: list[MovieData]) -> None:
    """
    Writes list of MovieData objects to a CSV file, either with enriched or
    plain/missing data.

    Parameters:
        csv_name (Path): Path to CSV file to be written to.

        data_list (list[MovieData]): List of MovieData objects to be written.
    """
    if data_list:
        with open(csv_path, "w") as csv_file:
            # Write header based on type of first item in data_list
            fieldnames = [f.name for f in dataclasses.fields(data_list[0])]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows((movie.flatten_values() for movie in data_list))


def wiki_feature_info(data: dict[str, Any], key: str) -> str | list[Any] | None:
    """
    Extracts movie information from a Wikidata query result.

    Parameters:
        data (dict): JSON response from a SPARQL query, see example in
        get_example_json_sparql_response().

        key (str): The key for the information to extract (e.g., 'item',
        'genreLabel', 'directorLabel').

    Returns:
        The formatted movie information, or None if the key is not present or no
        results are available. If the Key is present, return a list of unique
        genre labels if the key is 'genreLabel', otherwise return the movie ID
        of the first binding (in other words, the first row in query result).
    """
    if (
        len(data["results"]["bindings"]) < 1
        or key not in data["results"]["bindings"][0]
    ):
        return None
    if key == "genreLabel":
        return list(
            {
                d["genreLabel"]["value"]
                for d in data["results"]["bindings"]
                if "genreLabel" in d
            }
        )
    return str(data["results"]["bindings"][0][key]["value"].split("/")[-1])


def wiki_feature_optional_str(data: dict[str, Any], key: str) -> str | None:
    """Validates that we obtained a single (optional) string."""
    s = wiki_feature_info(data, key)
    assert isinstance(s, (str, NoneType)), s
    return s


def wiki_feature_genres(data: dict[str, Any], key: str) -> list[str]:
    """Validates that we obtained some sensible movie genres."""
    genres = wiki_feature_info(data, key)
    genres = genres or []
    assert isinstance(genres, list), genres
    for genre in genres:
        assert isinstance(genre, str)
    return genres


def format_sparql_query(title: str, year: int) -> str:
    """
    Formats a SPARQL query for Wiki data using the given title and year.
    """

    QUERY = """
        SELECT * WHERE {
            SERVICE wikibase:mwapi {
                bd:serviceParam wikibase:api "EntitySearch" ;
                                wikibase:endpoint "www.wikidata.org" ;
                                mwapi:search "%(Title)s" ;
                                mwapi:language "en" .
                ?item wikibase:apiOutputItem mwapi:item .
            }

            ?item wdt:P31/wdt:P279* wd:Q11424 .
            
            {
                # Get US release date
                ?item p:P577 ?releaseDateStatement .
                ?releaseDateStatement ps:P577 ?releaseDate .
                ?releaseDateStatement pq:P291 wd:Q30 .  
            }
            UNION
            {
                # Get unspecified release date
                ?item p:P577 ?releaseDateStatement .
                ?releaseDateStatement ps:P577 ?releaseDate .
                FILTER NOT EXISTS { ?releaseDateStatement pq:P291 ?country }
            }
        
            FILTER (YEAR(?releaseDate) = %(Year)d) .

            ?item rdfs:label ?itemLabel .
            FILTER (lang(?itemLabel) = "en") .

            OPTIONAL {
                ?item wdt:P136 ?genre .
                ?genre rdfs:label ?genreLabel .
                FILTER (lang(?genreLabel) = "en") .
            }

            OPTIONAL {?item wdt:P57 ?director.
                            ?director rdfs:label ?directorLabel.
                            FILTER (lang(?directorLabel) = "en")}

            SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
            }
    
        """
    return QUERY % {"Title": title, "Year": year}


def wiki_query(
    movie: MovieData,
    *,
    user_agent: str = USER_AGENT,
    query_endpoint: str = "https://query.wikidata.org/sparql",
) -> EnrichedMovieData | None:
    """
    Queries Wikidata for information about a movie.

    Parameters:
        movie (MovieData): A MovieData object to use in the sparql query.

        user_agent (str): Used to identify our script when sending requests to
        Wikidata SPARQL API.

    Returns:
        An EnrichedMovieData object containing information about the movie, or
        None if no results are found.

    Raises:
        WikidataServiceTimeoutException: If the Wikidata service times out.
    """
    SPARQL = format_sparql_query(movie.title, movie.year)

    tries = 0
    while True:
        try:
            log.info(f"Requesting id {movie.netflix_id} (try {tries})")
            response = requests.post(
                query_endpoint,
                headers={"User-Agent": user_agent},
                data={"query": SPARQL, "format": "json"},
                timeout=20,
            )
            break
        except requests.exceptions.Timeout:
            wait_time = 2**tries * 5
            time.sleep(wait_time)
            tries += 1
            if tries > 5:
                raise WikidataServiceTimeoutException(
                    f"Tried {tries} time, could not reach Wikidata "
                    f'(movie: "{movie.title}" {movie.year})'
                )

    response.raise_for_status()
    data = response.json()
    log.debug(data)

    if data["results"]["bindings"]:
        log.info(f'Found movie id {movie.netflix_id}: ("{movie.title}", {movie.year})')
        return EnrichedMovieData(
            **vars(movie),
            wikidata_id=str(wiki_feature_info(data, "item")),
            genres=wiki_feature_genres(data, "genreLabel"),
            director=wiki_feature_optional_str(data, "directorLabel"),
        )

    log.warning(
        f'Could not find movie id {movie.netflix_id}: ("{movie.title}", {movie.year})'
    )
    return None


def process_data(
    movie_data_path: Path,
    num_rows: int | None = None,
    output_missing_csv_path: Path | None = None,
) -> None:
    """
    Processes Netflix movie data by enriching it with information from Wikidata
    and writes the results to a CSV file.

    Parameters:
        num_rows (int): Number of rows to process. If None, all rows are
        processed.

        output_missing_csv_path (Path): If provided, movies that could not be
        matched will be written to a CSV at this path.

    Raises:
        FileNotFoundError: If the data directory or the movie data file does not
        exist.
    """

    data_dir = movie_data_path.parent
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Data directory does not exist at {data_dir}, please create a new directory containing the netflix prize dataset files\n"
            "https://archive.org/details/nf_prize_dataset.tar"
        )

    if not movie_data_path.exists():
        raise FileNotFoundError(
            f"{movie_data_path} not found, please download the netflix prize dataset and extract it into the data folder\n"
            "https://archive.org/details/nf_prize_dataset.tar"
        )

    total_count = 0
    missing_count = 0
    processed = []
    missing = []

    print(f"Processing {num_rows or 'all'} rows...")

    netflix_data = read_netflix_txt(movie_data_path, num_rows)
    for row in tqdm(netflix_data, total=num_rows):
        total_count += 1

        id, year, title = row
        if year == "NULL":
            log.warning(f"Skipping movie id {id}: (' {title} ', {year})")
            continue

        netflix_data = MovieData(id, title, int(year))
        if wiki_data := wiki_query(netflix_data):
            # wiki_query finds match, add to processed data
            processed.append(wiki_data)
        else:
            # Otherwise, is missing a match
            missing_count += 1
            if output_missing_csv_path:
                missing.append(netflix_data)

    output_csv = OUTPUT_DIR / "matches.csv"
    create_netflix_csv(output_csv, processed)
    if output_missing_csv_path:
        missing_csv = OUTPUT_DIR / output_missing_csv_path
        create_netflix_csv(missing_csv, missing)

    print(
        f"missing: {missing_count} ({missing_count / total_count * 100:.2f}%)\n"
        f"found: {total_count - missing_count} ({(total_count - missing_count) / total_count * 100:.2f}%)\n"
        f"total: {total_count}\n",
    )


@app.command()
def process(
    ctx: typer.Context,
    num_rows: int | None = typer.Option(
        DEFAULT_TEST_ROWS,
        "--num-rows",
        "-n",
        help="Number of rows to process. If --full is True, all rows are processed",
    ),
    missing_out_path: Path = typer.Option(
        None,
        "--missing-out-path",
        "-m",
        help=(
            "If provided, movies that could not be matched will be written to a "
            "CSV at this path, relative to the output directory."
        ),
    ),
    *,
    full: bool = typer.Option(
        False,
        "--full",
        "-f",
        help="Run processing on full dataset. Overrides --num_rows.",
    ),
) -> None:
    """Enrich Netflix data with Wikidata matches and write matches to CSV."""
    log.debug(ctx.obj)
    log_to_file = ctx.obj and ctx.obj.log_to_file
    # We redirect logs to stdout through tqdm to avoid breaking progress bar.
    # But when logging to file, we use nullcontext or tqdm will redirect logs
    # back to stdout.
    with nullcontext() if log_to_file else logging_redirect_tqdm():
        num_rows = None if full else num_rows
        try:
            process_data(
                FULL_TITLES_TXT, num_rows, output_missing_csv_path=missing_out_path
            )
        except Exception as e:
            # include fatal exceptions with traceback in logs
            if log_to_file:
                logging.exception("Uncaught exception", exc_info=True)
            raise e


if __name__ == "__main__":
    app()
