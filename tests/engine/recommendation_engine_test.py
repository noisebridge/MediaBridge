import os
import unittest

from mediabridge.db.connect import connect_to_mongo


class RecommendationEngineTest(unittest.TestCase):
    def test_connect_to_mongo(self) -> None:
        if os.environ.get("MONGODB_URI"):
            c = connect_to_mongo()
            self.assertEqual(0, len(list(c.list_collections())))

    def test_get_movie_id(self) -> None:
        0
