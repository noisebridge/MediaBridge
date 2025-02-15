import pandas as pd

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.connect import connect_to_mongo
from mediabridge.definitions import FULL_TITLES_TXT


def etl_mongo_movie_titles() -> None:
    columns = ["netflix_id", "year", "title"]
    df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=columns)
    rows = df.to_dict(orient="records")

    db = connect_to_mongo()
    movies_collection = db["movies"]
    movies_collection.insert_many(rows)
    db.client.close()
