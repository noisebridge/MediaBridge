import requests

"""
run main with:
PYTHONPATH=$(pwd) pipenv run python mediabridge/integrations/ollama_api.py
"""


def get_headers() -> dict:
    """Generates the headers required for making HTTP requests to the Ollama API"""
    return {"Content-Type": "application/json"}


def generate_prompt_response(model: str, prompt: str, url: str) -> str:
    """Sends a prompt to the Ollama API and returns the response as plain text"""
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, headers=get_headers(), json=payload)
    response.raise_for_status()  # raise an error if request fails
    response_json = response.json()
    return response_json.get("response", "")


if __name__ == "__main__":
    api_base_url = "https://ollama.tomato-pepper.uk/api"

    tags_url = f"{api_base_url}/tags"
    response = requests.get(tags_url, headers=get_headers())
    models_data = response.json().get("models", [])

    print("Available models:")
    for model in models_data:
        print("-", model["name"])

    model_name = "llama3:latest"
    input_prompt = "please say only the word 'Hello'"

    output_text = generate_prompt_response(
        model_name, input_prompt, f"{api_base_url}/generate"
    )
    print("Model response:", output_text)
