import requests
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth("ollamauser", "INSERT_PASSWORD_HERE")
api_base_url = "https://ollama.tomato-pepper.uk/api"


def _get_headers() -> dict[str, str]:
    """Generates the headers required for making HTTP requests to the Ollama API"""
    return {"Content-Type": "application/json"}


def generate_prompt_response(
    model: str = "llama3",
    prompt: str = "",
    url: str = f"{api_base_url}/generate",
) -> str:
    """Sends a prompt to the Ollama API and returns the response as plain text"""
    payload = {"model": model, "prompt": prompt, "stream": False}
    headers = _get_headers()
    response = requests.post(url, json=payload, headers=headers, auth=AUTH)
    response.raise_for_status()
    response_json = response.json()
    return response_json["response"]
