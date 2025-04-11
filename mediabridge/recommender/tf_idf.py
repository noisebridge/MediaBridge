import sqlite3

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database setup
DB_FILE = "movies.db"


def create_database():
    """Create the SQLite database and movies table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the movies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            genres TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_movies(data):
    """Insert movie data into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Insert data into the movies table
    cursor.executemany(
        """
        INSERT INTO movies (movie_id, title, genres, description)
        VALUES (?, ?, ?, ?)
    """,
        data,
    )
    conn.commit()
    conn.close()


def fetch_movies():
    """Fetch all movies from the database as a DataFrame."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    return df


def compute_similarity_matrix(data):
    """Compute the TF-IDF similarity matrix for movie descriptions."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(data["description"])
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix


def recommend_multiple_items(titles, data, similarity_matrix, top_k=3):
    """Recommend movies based on input titles."""
    # Find indices for all input movies
    indices = [data[data["title"] == title].index[0] for title in titles]

    # Compute the mean similarity scores across the selected movies
    aggregated_scores = np.mean(similarity_matrix[indices, :], axis=0)

    # Rank items by aggregated similarity scores, excluding input movies
    similar_items = aggregated_scores.argsort()[::-1]
    similar_items = [i for i in similar_items if i not in indices]

    # Return top-k recommendations
    recommendations = data.iloc[similar_items[:top_k]]
    return recommendations[["title", "genres", "description"]]


# Main script
if __name__ == "__main__":
    # Create the database and table
    create_database()

    # Fetch movies from the database
    data = fetch_movies()

    # Compute the similarity matrix
    similarity_matrix = compute_similarity_matrix(data)

    # Prompt the user for recommendations
    while True:
        movie_names = input(
            "Enter movie name(s) for recommendations separated by commas (or type 'exit' to quit): "
        )

        if movie_names.lower() == "exit":
            break

        # Split input into individual movie titles and remove any extra spaces
        titles = [name.strip() for name in movie_names.split(",")]

        # Check if all movies exist in the dataset
        missing_movies = [
            title for title in titles if title not in data["title"].values
        ]
        if missing_movies:
            print(
                f"These movie(s) were not found: {', '.join(missing_movies)}. Please try again."
            )
        else:
            print("\nRecommendations based on your input movies:")
            recommendations = recommend_multiple_items(titles, data, similarity_matrix)
            print(recommendations, "\n")
