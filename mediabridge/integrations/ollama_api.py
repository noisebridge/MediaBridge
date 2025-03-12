import requests

"""
run main with:
PYTHONPATH=$(pwd) pipenv run python mediabridge/integrations/ollama_api.py
"""


def get_headers() -> dict:
    """Generates the headers required for making HTTP requests to the Ollama API"""
    return {"Content-Type": "application/json"}


if __name__ == "__main__":
    url = "https://ollama.tomato-pepper.uk/api/tags"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    print(response.json())
