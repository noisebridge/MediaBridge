import pandas as pd

from mediabridge.db.connect import connect_to_mongo
from mediabridge.definitions import FULL_TITLES_TXT


def etl_mongo_movie_titles() -> None:  # pragma: no cover
    df = pd.read_csv(FULL_TITLES_TXT)
    df["netflix_id"] = df.netflix_id.astype(str)
    rows = df.to_dict(orient="records")
    print(f"{len(rows)} rows ", end="", flush=True)

    db = connect_to_mongo()
    movies_collection = db["movies"]
    movies_collection.delete_many({})  # actually, this is "delete all"

    movies_collection.insert_many(rows)
    movies_collection.close()
    print("inserted")
