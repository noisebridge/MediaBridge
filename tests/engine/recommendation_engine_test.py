import os
import unittest

import pandas as pd

from mediabridge.db.connect import connect_to_mongo
from mediabridge.definitions import DATA_DIR, OUTPUT_DIR
from mediabridge.engine.recommendation_engine import RecommendationEngine


def etl_mongo_movie_titles() -> None:
    df = pd.read_csv(DATA_DIR / "movie_titles.csv")
    df["netflix_id"] = df.netflix_id.astype(str)
    rows = df.to_dict(orient="records")
    print(rows)

    client = connect_to_mongo()
    movies_collection = client["movies"]

    movies_collection.insert_many(rows)


# In a github Actions CI environment, we will be "disabled".
_enabled = bool(os.getenv("MONGODB_URI"))


class RecommendationEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        if _enabled:
            self.engine = RecommendationEngine(
                ["1", "2"],
                OUTPUT_DIR / "interaction_matrix.pkl",
            )

    def tearDown(self) -> None:
        if _enabled:
            self.engine.db.client.close()

    def test_connect_to_mongo(self) -> None:
        if _enabled:
            db = connect_to_mongo()
            num_collections = len(list(db.list_collections()))
            if num_collections == 0:
                etl_mongo_movie_titles()
            db.client.close()

    def test_get_movie_id(self) -> None:
        self.assertEqual("1", self.engine.get_movie_id("Dinosaur Planet"))
