import unittest

from mediabridge.integrations.ollama_api import generate_prompt_response

"""
run in isolation with: 
PYTHONPATH=$(pwd) pipenv run python -m unittest tests/integrations/ollama_api_test.py
"""


class TestOllamaAPI(unittest.TestCase):
    def test_get_response(self):
        input_prompt = "please say only the word 'Hello'"
        response = generate_prompt_response(prompt=input_prompt)
        self.assertEqual(response.strip(), "Hello")
