from pathlib import Path

from mediabridge.definitions import PROJECT_DIR
from mediabridge.integrations.ollama_api import generate_prompt_response

ADJ_DATA_DIR = PROJECT_DIR / "mediabridge" / "data"

f1 = open(ADJ_DATA_DIR / "movie_titles.txt", "r", encoding="latin1")

start_line = 16

for i, raw_line in enumerate(f1):
    if i < start_line:
        continue  # Skip until we hit the start line

    line = raw_line.strip().split(",")
    prompt = f"Write a paragraph description for the {line[1]} production '{line[2]}' — no introductions, titles, or extra formatting."
    print(f"writing description for {line[2]}...")

    response = generate_prompt_response(prompt=prompt)
    f2 = open(
        ADJ_DATA_DIR / "movie_titles_plus_descriptions.txt", "a", encoding="latin1"
    )
    f2.write(f"{line[0]},{line[1]},{line[2]},{response}\n")
    f2.close()

f1.close()
