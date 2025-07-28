import pickle
import shutil
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, text

from mediabridge.data_processing.interaction_matrix import (
    MAX_USER_ID,
    NUM_MOVIES,
    create_matrix,
    save_matrix,
)
from mediabridge.definitions import OUTPUT_DIR

TEST_OUT = OUTPUT_DIR / "test_data"
TEST_DB_FILE = TEST_OUT / "test.db"


class InteractionMatrixTest(unittest.TestCase):
    def setUp(self):
        TEST_OUT.mkdir(parents=True, exist_ok=True)

        self.test_engine = create_engine(f"sqlite:///{TEST_DB_FILE}")
        with self.test_engine.connect() as conn:
            conn.execute(text("CREATE TABLE rating (user_id, movie_id, rating)"))
            conn.execute(
                text(
                    "INSERT INTO rating (user_id, movie_id, rating) "
                    "VALUES (10, 1, 5), (10, 2, 4), (20, 1, 3), (20, 2, 2), (99, 2, 1)"
                )
            )
            conn.commit()

    def tearDown(self):
        shutil.rmtree(TEST_OUT, ignore_errors=True)

    def _assert_matrix(self, matrix):
        matrix = matrix.todok()
        self.assertIsNotNone(matrix)
        self.assertEqual(matrix.shape, (MAX_USER_ID + 1, NUM_MOVIES + 1))
        self.assertEqual(1, matrix[10, 1])
        self.assertEqual(0.5, matrix[10, 2])
        self.assertEqual(0, matrix[20, 1])
        self.assertEqual(-0.5, matrix[20, 2])
        self.assertEqual(-1, matrix[99, 2])
        self.assertEqual(0, matrix[0, 0])

    @patch("mediabridge.data_processing.interaction_matrix.get_engine")
    def test_create_matrix(self, mock_get_engine):
        mock_get_engine.return_value = self.test_engine

        actual = create_matrix()

        self._assert_matrix(actual)

    @patch("mediabridge.data_processing.interaction_matrix.get_engine")
    def test_save_matrix(self, mock_get_engine):
        mock_get_engine.return_value = self.test_engine

        output_file = TEST_OUT / "interaction_matrix.pkl"
        save_matrix(ctx=None, debug=True, output_file=output_file)

        with open(output_file, "rb") as f:
            matrix = pickle.load(f)

        self._assert_matrix(matrix)
