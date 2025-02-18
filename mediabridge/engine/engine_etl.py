import pandas as pd

from mediabridge.db.connect import connect_to_mongo
from mediabridge.definitions import DATA_DIR


def etl_mongo_movie_titles() -> None:  # pragma: no cover
    df = pd.read_csv(DATA_DIR / "movie_titles.csv")
    df["netflix_id"] = df.netflix_id.astype(str)
    rows = df.to_dict(orient="records")
    print(f"{len(rows)} rows ", end="", flush=True)

    client = connect_to_mongo()
    movies_collection = client["movies"]
    movies_collection.delete_many({})  # actually, this is "delete all"

    movies_collection.insert_many(rows)
    print("inserted")
