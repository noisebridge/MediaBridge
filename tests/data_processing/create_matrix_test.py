import unittest
from unittest.mock import patch

from mediabridge.data_processing.interaction_matrix import save_matrix


class CreateMatrixTest(unittest.TestCase):

    # This is a five minute test when run against all user ratings.
    # @mark_slow_integration_test  # type: ignore
    def test_save_matrix(self) -> None:
        with patch("typer.Context") as MockContext:
            save_matrix(MockContext(), max_user_id=94)
