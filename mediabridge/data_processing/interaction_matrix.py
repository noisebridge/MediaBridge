import os
import pickle
from collections.abc import Generator
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix, dok_matrix
from tqdm import tqdm

from mediabridge.definitions import DATA_DIR, LIGHTFM_MODEL_PKL, OUTPUT_DIR
from MediaBridge.mediabridge.recommender.import_utils import import_lightfm_silently


def list_rating_files(directory_path: Path) -> Generator[str, None, None]:
    """List of files in the directory that start with mv_."""
    for f in os.listdir(directory_path):
        if f.startswith("mv_"):
            yield os.path.join(directory_path, f)


def create_interaction_matrix(
    directory_path: Path,
    num_users: int,
    num_movies: int,
) -> coo_matrix:
    interaction_matrix = dok_matrix((num_users, num_movies), dtype=np.int8)
    user_mapper = {}
    current_user_index = 0

    for file_path in tqdm(sorted(list_rating_files(directory_path)), smoothing=0.001):
        with open(file_path, "r") as file:
            movie_id = int(file.readline().strip().replace(":", ""))
            movie_idx = movie_id - 1

            for line in file:
                user_id, rating = map(int, line.strip().split(",")[:2])

                if rating < 4:
                    continue

                if user_id not in user_mapper:
                    user_mapper[user_id] = current_user_index
                    current_user_index += 1

                user_idx = user_mapper[user_id]
                interaction_matrix[user_idx, movie_idx] = rating

    return coo_matrix(interaction_matrix)


def save_matrix(matrix: coo_matrix, output_file: Path) -> None:
    with open(output_file, "wb") as f:
        pickle.dump(matrix, f)
    print(f"Interaction matrix saved to {output_file}")


def main() -> None:
    """Main entry point to create and save the interaction matrix."""

    # Configurations
    output_file = OUTPUT_DIR / "interaction_matrix.pkl"
    output_file.parent.mkdir(exist_ok=True)

    # Number of users and movies
    num_users = 480_189
    num_movies = 17_770

    # Process Data
    interaction_matrix = create_interaction_matrix(DATA_DIR, num_users, num_movies)

    # Save Data
    LightFM = import_lightfm_silently()
    model = LightFM()
    model.fit(interaction_matrix)  # This takes ~ 27 seconds.
    with open(LIGHTFM_MODEL_PKL, "wb") as f:
        pickle.dump(model, f)
    save_matrix(interaction_matrix, output_file)


if __name__ == "__main__":
    main()
