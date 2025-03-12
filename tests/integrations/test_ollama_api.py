import unittest

from mediabridge.integrations.ollama_api import get_headers

"""
run in isolation with: 
PYTHONPATH=$(pwd) pipenv run python -m unittest tests/integrations/test_ollama_api.py
"""


class TestOllamaAPI(unittest.TestCase):
    def test_get_headers(self):
        expected_headers = {"Content-Type": "application/json"}
        self.assertEqual(get_headers(), expected_headers)


if __name__ == "__main__":
    unittest.main()
