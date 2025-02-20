import pandas as pd

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.connect import connect_to_mongo
from mediabridge.definitions import FULL_TITLES_TXT


def etl_mongo_movie_titles() -> None:  # pragma: no cover
    cols = ["netflix_id", "year", "title"]
    df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=cols)
    df["netflix_id"] = df.netflix_id.astype(str)
    rows = df.to_dict(orient="records")
    print(f"{len(rows)} rows ", end="", flush=True)

    db = connect_to_mongo()
    movies_collection = db["movies"]
    movies_collection.delete_many({})  # actually, this is "delete all"

    movies_collection.insert_many(rows)
    movies_collection.close()
    print("inserted")
