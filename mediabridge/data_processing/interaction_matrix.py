import os
import pickle

import numpy as np


def list_rating_files(directory_path):
    """List of files in the directory that start with mv_."""
    return sorted([f for f in os.listdir(directory_path) if f.startswith("mv_")])


def create_interaction_matrix(directory_path, num_users, num_movies, files):
    interaction_matrix = np.zeros((num_users, num_movies), dtype=np.int8)
    user_mapper = {}
    current_user_index = 0

    for filename in files:
        with open(os.path.join(directory_path, filename), "r") as file:
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
                interaction_matrix[user_idx, movie_idx] = rating

    return interaction_matrix


def save_matrix(matrix, output_file):
    with open(output_file, "wb") as f:
        pickle.dump(matrix, f)
    print(f"Interaction matrix saved to {output_file}")


def main():
    """Main entry point to create and save the interaction matrix."""
    # from db.mongo_connection import get_db_connection
    # from db.movie_storage import insert_movie_data

    # Configurations
    data_directory = os.path.join(os.path.dirname(__file__), "../../data/")
    ratings_directory = os.path.join(data_directory, "training_set/")
    output_directory = os.path.join(data_directory, "../output/")
    output_file = os.path.join(output_directory, "interaction_matrix.pkl")

    # Number of users and movies
    num_users = 480189  # Example: Replace with actual value
    num_movies = 17770  # Example: Replace with actual value

    # Step 1: Load Data
    movie_data = list_rating_files(ratings_directory)

    # Step 2: Process Data
    interaction_matrix = create_interaction_matrix(
        data_directory, num_users, num_movies, movie_data
    )

    # Step 3: Save Data
    save_matrix(interaction_matrix, output_file)

    # Step 4: Store Movies in MongoDB
    # db = get_db_connection(uri=mongo_uri, db_name=db_name)
    # insert_movie_data(db, 'movies', movie_data)


if __name__ == "__main__":
    main()
