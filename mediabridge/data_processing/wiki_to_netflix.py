import csv
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

import requests
from tqdm import tqdm


class WikidataServiceTimeoutException(Exception):
    pass


@dataclass
class MovieData:
    movie_id: Optional[str]
    genre: List[str]
    director: Optional[str]


log = logging.getLogger(__name__)

# need Genres, Directors, Title, year?

data_dir = os.path.join(os.path.dirname(__file__), "../../data")
out_dir = os.path.join(os.path.dirname(__file__), "../../out")
user_agent = "Noisebridge MovieBot 0.0.1/Audiodude <audiodude@gmail.com>"


def read_netflix_txt(txt_file, test):
    """
    Reads and processes a Netflix text file.

    Parameters:
    txt_file (str): Path to the Netflix text file
    test (Bool): When true, runs the functon in test mode
    """
    num_rows = None
    if test:
        num_rows = 10

    with open(txt_file, "r", encoding="ISO-8859-1") as netflix_data:
        for i, line in enumerate(netflix_data):
            if num_rows is not None and i >= num_rows:
                break
            yield line.rstrip().split(",", 2)


def create_netflix_csv(csv_name, data_list):
    """
    Writes data to a Netflix CSV file.

    Parameters:
    csv_name (str): Name of CSV file to be created
    data_list (list): Row of data to be written to CSV file
    """
    with open(csv_name, "w") as netflix_csv:
        csv.writer(netflix_csv).writerows(data_list)


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


def wiki_query(data_csv, user_agent):
    """
    Formats SPARQL query for Wiki data

    Parameters:
    data_csv (list of lists): Rows of movie data with [movie ID, release year, title].
    user_agent (str): used to identify our script when sending requests to Wikidata SPARQL API.

    Returns:
        list of WikiMovieData: A list of movieData instances with movie IDs, genres, and directors.
    """
    wiki_data_list = []

    for row in tqdm(data_csv):
        id, year, title = row
        if year is None:
            continue

        SPARQL = format_sparql_query(title, int(year))
        # logging.debug(SPARQL)

        tries = 0
        while True:
            try:
                log.info("Requesting ' %s ' %s (try %i)", title, year, tries)
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
                        f"(movie: {title} {year})"
                    )

        response.raise_for_status()
        data = response.json()
        log.debug(data)

        if not data["results"]["bindings"]:
            log.warning("Could not find movie id %s (' %s ', %s)", id, title, year)

        wiki_data_list.append(
            MovieData(
                movie_id=wiki_feature_info(data, "item"),
                genre=wiki_feature_info(data, "genreLabel"),
                director=wiki_feature_info(data, "directorLabel"),
            )
        )

    return wiki_data_list


def process_data(test=False):
    """
    Processes Netflix movie data by enriching it with information from Wikidata and writes the results to a CSV file.
    Netflix data was conveted from a generator to a list to avoid exaustion. was running into an issue where nothing would print to CSV file
    """
    missing_count = 0
    processed_data = []

    netflix_data = list(
        read_netflix_txt(os.path.join(data_dir, "movie_titles.txt"), test)
    )

    netflix_csv = os.path.join(out_dir, "movie_titles.csv")

    enriched_movies = wiki_query(netflix_data, user_agent)

    num_rows = len(enriched_movies)

    for index, row in enumerate(netflix_data):
        netflix_id, year, title = row
        movie_data = enriched_movies[index]
        if movie_data.movie_id is None:
            missing_count += 1
        if movie_data.genre:
            genres = "; ".join(movie_data.genre)
        else:
            genres = ""
        if movie_data.director:
            director = movie_data.director
        else:
            director = ""
        movie = [
            netflix_id,
            movie_data.movie_id,
            title,
            year,
            genres,
            director,
        ]
        processed_data.append(movie)

    print("Processed Data:")
    for movie in processed_data:
        print(movie)

    create_netflix_csv(netflix_csv, processed_data)

    print(f"missing:  {missing_count} ({missing_count / num_rows * 100:.2f}%)")
    print(
        f"found: {num_rows - missing_count} ({(num_rows - missing_count) / num_rows * 100:.2f}%)"
    )
    print(f"total: {num_rows}")


if __name__ == "__main__":
    # Test is true if no argument is passed or if the first argument is not '--prod'.
    test = len(sys.argv) < 2 or sys.argv[1] != "--prod"
    process_data(test=test)
