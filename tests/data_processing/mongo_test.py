import unittest

""" run with: PYTHONPATH=$(pwd) pipenv run python -m unittest tests/data_processing/mongo_test.py """


class TestMongo(unittest.TestCase):
    def test_placeholder(self):
        """A placeholder test that always passes."""
        self.assertTrue(True)
