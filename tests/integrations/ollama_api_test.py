import unittest
from unittest.mock import MagicMock, patch

from mediabridge.integrations.ollama_api import generate_prompt_response

"""
run in isolation with: 
PYTHONPATH=$(pwd) pipenv run python -m unittest tests/integrations/ollama_api_test.py
"""


class TestOllamaAPI(unittest.TestCase):
    @patch("mediabridge.integrations.ollama_api.requests")
    def test_get_response(self, mock_requests: MagicMock) -> None:
        mock_requests.post.return_value.status_code = 200
        mock_requests.post.return_value.json.return_value = {
            "model": "llama3",
            "response": "Hello",
            "done": True,
        }

        result = generate_prompt_response(
            model="llama3",
            prompt="please say only the word 'Hello'",
            url="https://mocked-url/api/generate",
        )

        self.assertEqual(result.strip(), "Hello")
