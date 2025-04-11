import json

from mediabridge.definitions import PROJECT_DIR
from mediabridge.integrations.ollama_api import generate_prompt_response

ADJ_DATA_DIR = PROJECT_DIR / "mediabridge" / "data"

f1 = open(ADJ_DATA_DIR / "movie_titles.txt", "r", encoding="latin1")

start_line = 0

for i, raw_line in enumerate(f1):
    if i < start_line:
        continue  # Skip until we hit the start line

    line = raw_line.strip().split(",", maxsplit=2)

    movie_id = line[0]
    year = line[1]
    title = line[2]

    print(f"writing description for {title}...")

    prompt = f"Write a paragraph description for the {year} production '{title}' — no introductions, titles, or extra formatting."
    response = generate_prompt_response(prompt=prompt)

    movie_data = {
        "id": movie_id,
        "year": year,
        "title": title,
        "description": response.strip(),
    }

    with open(
        ADJ_DATA_DIR / "movie_titles_plus_descriptions.jsonl", "a", encoding="utf-8"
    ) as f2:
        f2.write(json.dumps(movie_data, ensure_ascii=False) + "\n")

f1.close()
