import unittest
from unittest.mock import patch

from mediabridge.data_processing.interaction_matrix import save_matrix
from tests.util.slow import mark_slow_integration_test


class CreateMatrixTest(unittest.TestCase):

    # This is a five minute test.
    @mark_slow_integration_test  # type: ignore
    def test_save_matrix(self) -> None:
        with patch("typer.Context") as MockContext:
            save_matrix(MockContext())
