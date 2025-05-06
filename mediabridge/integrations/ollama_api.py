import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

api_base_url = "https://ollama.tomato-pepper.uk/api"


def _get_headers() -> dict[str, str]:
    """Generates the headers required for making HTTP requests to the Ollama API"""
    return {"Content-Type": "application/json"}


def _get_auth() -> HTTPBasicAuth:
    """loads the authentication credentials for the Ollama API."""
    username = os.getenv("OLLAMA_USERNAME")
    password = os.getenv("OLLAMA_PASSWORD")
    if not username:
        raise ValueError("OLLAMA_USERNAME is not set in the .env file.")
    if not password:
        raise ValueError("OLLAMA_PASSWORD is not set in the .env file.")
    return HTTPBasicAuth(username, password)


def generate_prompt_response(
    model: str = "llama3",
    prompt: str = "",
    url: str = f"{api_base_url}/generate",
) -> str:
    """Sends a prompt to the Ollama API and returns the response as plain text"""
    payload = {"model": model, "prompt": prompt, "stream": False}
    headers = _get_headers()
    auth = _get_auth()
    response = requests.post(url, json=payload, headers=headers, auth=auth)
    response.raise_for_status()
    response_json = response.json()
    return f'{response_json["response"]}'
