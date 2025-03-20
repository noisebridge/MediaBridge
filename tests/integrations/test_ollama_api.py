import unittest

from mediabridge.integrations.ollama_api import generate_prompt_response, get_headers

"""
run in isolation with: 
PYTHONPATH=$(pwd) pipenv run python -m unittest tests/integrations/test_ollama_api.py
"""


class TestOllamaAPI(unittest.TestCase):
    def test_get_headers(self):
        expected_headers = {"Content-Type": "application/json"}
        self.assertEqual(get_headers(), expected_headers)

    def test_get_response(self):
        api_base_url = "https://ollama.tomato-pepper.uk/api"
        model_name = "llama3:latest"
        input_prompt = "please say only the word 'Hello'"
        response = generate_prompt_response(
            model_name, input_prompt, f"{api_base_url}/generate"
        )
        self.assertEqual(response.strip(), "Hello")


if __name__ == "__main__":
    unittest.main()
