import os
import unittest

from mediabridge.db.connect import connect_to_mongo
from mediabridge.definitions import OUTPUT_DIR
from mediabridge.engine.engine_etl import etl_mongo_movie_titles
from mediabridge.engine.recommendation_engine import RecommendationEngine

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
        if _enabled:
            self.assertEqual("1", self.engine.get_movie_id("Dinosaur Planet"))

    def test_get_movie_title(self) -> None:
        if _enabled:
            # NB: passing in the integer 1 instead of the str "1" will definitely fail
            self.assertEqual("Dinosaur Planet", self.engine.get_movie_title("1"))
            self.assertEqual("The Green Mile", self.engine.get_movie_title("16377"))
