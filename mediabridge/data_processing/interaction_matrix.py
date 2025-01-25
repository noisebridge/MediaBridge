import os
import pickle

import numpy as np
from scipy.sparse import coo_matrix

from mediabridge.definitions import DATA_DIR


def list_rating_files(directory_path):
    """List of files in the directory that start with mv_."""
    for f in os.listdir(directory_path):
        if f.startswith("mv_"):
            yield os.path.join(directory_path, f)


def create_interaction_matrix(directory_path, num_users, num_movies):
    im = interaction_matrix = coo_matrix((num_users, num_movies), dtype=np.int8)
    user_mapper = {}
    current_user_index = 0

    for file_path in list_rating_files(directory_path):
        with open(file_path, "r") as file:
            movie_id = int(file.readline().strip().replace(":", ""))
            movie_idx = movie_id - 1

            for line in file:
                user_id, rating, _ = line.strip().split(",")
                user_id = int(user_id)
                rating = int(rating)

                if rating < 4:
                    continue

                if user_id not in user_mapper:
                    user_mapper[user_id] = current_user_index
                    current_user_index += 1

                user_idx = user_mapper[user_id]
                im[user_idx, movie_idx] = rating  # type: ignore [reportIndexIssue]

    return interaction_matrix


def save_matrix(matrix, output_file):
    with open(output_file, "wb") as f:
        pickle.dump(matrix, f)
    print(f"Interaction matrix saved to {output_file}")


def main():
    """Main entry point to create and save the interaction matrix."""

    # Configurations
    output_file = DATA_DIR.parent / "output/interaction_matrix.pkl"
    output_file.parent.mkdir(exist_ok=True)

    # Number of users and movies
    num_users = 480_189
    num_movies = 17_770

    # Process Data
    interaction_matrix = create_interaction_matrix(DATA_DIR, num_users, num_movies)

    # Save Data
    save_matrix(interaction_matrix, output_file)


if __name__ == "__main__":
    main()
