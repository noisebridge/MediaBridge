import json

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from mediabridge.definitions import DATA_DIR


def recommend_multiple_items(
    titles: list[str],
    data: pd.DataFrame,
    similarity_matrix: NDArray[np.float64],
    top_k: int = 5,
    alpha: float = 0.5,
    beta: float = 0.7,
    gamma: float = 2.0,
) -> pd.DataFrame:
    """
    Recommend movies based on multiple input titles.

    Parameters:
    - titles: list of input movie titles
    - data: DataFrame containing all movie data
    - similarity_matrix: 2D numpy array of pairwise similarities
    - top_k: number of recommendations to return
    - alpha (float): Weight applied to the minimum similarity score across input titles.
        Higher alpha encourages recommendations that are consistently similar to all input titles,
        helping to avoid items that only relate to a single input.
    - beta (float): Weight applied to the maximum similarity score across input titles.
        This acts as a penalty for recommendations that are only strongly similar to one input title.
        Higher beta discourages one-sided matches.
    - gamma (float): Weight applied to the standard deviation of similarity scores across input titles.
        A higher gamma penalizes candidates with uneven similarity — i.e., very similar to one input and
        dissimilar to others. This promotes more balanced, blended recommendations.
    """

    # Find indices for all input movies
    indices = [data[data["title"] == title].index[0] for title in titles]

    # Compute similarity scores for all inputs
    similarity_scores = similarity_matrix[indices, :]  # shape: (num_inputs, num_movies)

    # Compute mean, min, and max similarity per candidate
    mean_sim = np.mean(similarity_scores, axis=0)
    min_sim = np.min(similarity_scores, axis=0)
    max_sim = np.max(similarity_scores, axis=0)

    # Hybrid score: prioritize candidates with decent similarity to *all* inputs
    std_sim = np.std(similarity_scores, axis=0)
    scores = mean_sim + (alpha * min_sim) - (beta * max_sim) - (gamma * std_sim)

    # Exclude input titles from results
    scores[indices] = -1  # Or any low number to push them to bottom

    # Get top-k recommendation indices
    top_indices = np.argsort(scores)[::-1][:top_k]
    recommendations = data.iloc[top_indices]

    # Format corrections
    recommendations["year"] = recommendations["year"].astype("Int64")
    recommendations["description"] = recommendations["description"].apply(
        lambda d: d[:75] + "..." if isinstance(d, str) and len(d) > 75 else d
    )
    return recommendations[["title", "year", "description"]]


def transform(data: pd.DataFrame) -> NDArray[np.float64]:
    """Expects a pandas Dataframe with a 'description' column. Returns a TF-IDF matrix and the cosine similarity matrix."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(data["description"])
    sim = cosine_similarity(tfidf_matrix)
    return np.ndarray(sim)


def create_dataframe() -> pd.DataFrame:
    """Function that generates a dataframe from movie_titles_plus Descriptions.jsonl"""
    input_path = DATA_DIR / "movie_titles_plus_descriptions.jsonl"

    with open(input_path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    df = pd.DataFrame(data)
    return df
