import csv
import dataclasses
import logging
import time
from contextlib import nullcontext

import requests
import typer
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from mediabridge.dataclasses import EnrichedMovieData, MovieData
from mediabridge.definitions import DATA_DIR, OUTPUT_DIR

USER_AGENT = "Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>"
DEFAULT_TEST_ROWS = 100


class WikidataServiceTimeoutException(Exception):
    pass


app = typer.Typer()
log = logging.getLogger(__name__)


def read_netflix_txt(txt_file, num_rows=None):
    """
    Reads and processes a Netflix text file.

    Parameters:
    txt_file (str): Path to the Netflix text file
    num_rows (int): Number of rows to read from the file, defaults to all
    """
    with open(txt_file, "r", encoding="ISO-8859-1") as netflix_data:
        for i, line in enumerate(netflix_data):
            if num_rows is not None and i >= num_rows:
                break
            yield line.rstrip().split(",", 2)


def create_netflix_csv(csv_path, data_list: list[MovieData]):
    """
    Writes list of MovieData objects to a CSV file, either enriched or plain.

    Parameters:
    csv_name (str): Name of CSV file to be created
    data_list (list): List of data to be written to CSV file
    """
    with open(csv_path, "w") as netflix_csv:
        if data_list:
            # Write header based on type of first item in data_list
            csv.writer(netflix_csv).writerow(
                (f.name for f in dataclasses.fields(data_list[0]))
            )
            # Write data
            csv.writer(netflix_csv).writerows(
                (movie.flatten_values() for movie in data_list)
            )


def wiki_feature_info(data, key):
    """
    Extracts movie information from a Wikidata query result.

    Parameters:
    data (dict): JSON response from a SPARQL query, see example in get_example_json_sparql_response().
    key (str): The key for the information to extract (e.g., 'item', 'genreLabel', 'directorLabel').

    Returns:
        None: If the key is not present or no results are available.
        list: If the key is 'genreLabel', returns a list of unique genre labels.
        String: If the Key is present, return the movie ID of the first binding, in other words the first row in query result
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
    return data["results"]["bindings"][0][key]["value"].split("/")[-1]


def format_sparql_query(title, year):
    """
    Formats SPARQL query for Wiki data

    Parameters:
    title (str): name of content to query
    year (int): release year of the movie

    Returns:
    SPARQL Query (str): formatted string with movie title and year
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


def wiki_query(movie: MovieData, user_agent: str) -> EnrichedMovieData | None:
    """
    Queries Wikidata for information about a movie.

    Parameters:
    movie (MovieData): A MovieData object to use in the sparql query.
    user_agent (str): Used to identify our script when sending requests to Wikidata SPARQL API.

    Returns:
    EnrichedMovieData: An EnrichedMovieData object containing information about the movie.
    """
    SPARQL = format_sparql_query(movie.title, movie.year)
    # logging.debug(SPARQL)

    tries = 0
    while True:
        try:
            log.info(f"Requesting id {movie.netflix_id} (try {tries})")
            response = requests.post(
                "https://query.wikidata.org/sparql",
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
                    f"(movie: {movie.title} {movie.year})"
                )

    response.raise_for_status()
    data = response.json()
    log.debug(data)

    if not data["results"]["bindings"]:
        log.warning(
            f"Could not find movie id {movie.netflix_id}: (' {movie.title} ', {movie.year})"
        )
    else:
        log.info(
            f"Found movie id {movie.netflix_id}: (' {movie.title} ', {movie.year})"
        )
        return EnrichedMovieData(
            **movie.__dict__,
            wikidata_id=wiki_feature_info(data, "item"),
            genres=wiki_feature_info(data, "genreLabel"),
            director=wiki_feature_info(data, "directorLabel"),
        )

    return None


def process_data(num_rows=None, output_missing_csv_path=None):
    """
    Processes Netflix movie data by enriching it with information from Wikidata and writes the results to a CSV file.
    Netflix data was conveted from a generator to a list to avoid exaustion. was running into an issue where nothing would print to CSV file

    num_rows (int): Number of rows to process. If None, all rows are processed.
    output_missing_csv_path (str): If provided, movies that could not be matched will be written to a CSV at this path.
    """

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Data directory does not exist at {DATA_DIR}, please create a new directory containing the netflix prize dataset files\n"
            "https://archive.org/details/nf_prize_dataset.tar"
        )

    movie_data_path = DATA_DIR.joinpath("movie_titles.txt")

    if not movie_data_path.exists():
        raise FileNotFoundError(
            f"{movie_data_path} not found, please download the netflix prize dataset and extract it into the data folder\n"
            "https://archive.org/details/nf_prize_dataset.tar"
        )

    missing_count = 0
    processed_data = []
    missing = []

    print(f"Processing {num_rows or 'all'} rows...")

    netflix_data = read_netflix_txt(movie_data_path, num_rows)
    for row in tqdm(netflix_data, total=num_rows):
        id, year, title = row
        netflix_data = MovieData(int(id), title, int(year))
        if wiki_data := wiki_query(netflix_data, USER_AGENT):
            # wiki_query finds match, add to processed data
            processed_data.append(wiki_data)
        else:
            # Otherwise, is missing a match
            missing_count += 1
            if output_missing_csv_path:
                missing.append(netflix_data)

    output_csv = OUTPUT_DIR.joinpath("matches.csv")
    create_netflix_csv(output_csv, processed_data)
    if output_missing_csv_path:
        missing_csv = OUTPUT_DIR.joinpath(output_missing_csv_path)
        create_netflix_csv(missing_csv, missing)

    print(
        f"missing: {missing_count} ({missing_count / num_rows * 100:.2f}%)\n"
        f"found: {num_rows - missing_count} ({(num_rows - missing_count) / num_rows * 100:.2f}%)\n"
        f"total: {num_rows}\n",
    )


@app.command()
def process(
    ctx: typer.Context,
    full: bool = typer.Option(
        False,
        "--full",
        "-f",
        help="Run processing on full dataset. Overrides --num_rows.",
    ),
    num_rows: int = typer.Option(
        DEFAULT_TEST_ROWS,
        "--num_rows",
        "-n",
        help="Number of rows to process. If --full is True, all rows are processed",
    ),
    missing_out_path: str = typer.Option(
        None,
        "--missing_out_path",
        "-m",
        help=(
            "If provided, movies that could not be matched will be written to a "
            "CSV at this path, relative to the output directory."
        ),
    ),
):
    """Enrich Netflix data with Wikidata matches."""
    log.debug(ctx.obj)
    # We redirect logs to stdout through tqdm to avoid breaking progress bar.
    # But when logging to file, we use nullcontext or tqdm will redirect logs
    # back to stdout.
    with nullcontext() if ctx.obj and ctx.obj.log else logging_redirect_tqdm():
        num_rows = None if full else num_rows
        try:
            process_data(num_rows, output_missing_csv_path=missing_out_path)
        except Exception as e:
            # include fatal exceptions with traceback in logs
            if ctx.obj and ctx.obj.log:
                logging.exception("Uncaught exception")
            raise e


if __name__ == "__main__":
    app()
