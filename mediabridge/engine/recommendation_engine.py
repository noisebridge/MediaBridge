import pickle
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from beartype import beartype
from numpy.typing import NDArray
from scipy.sparse import coo_matrix

from mediabridge.db.connect import connect_to_mongo
from mediabridge.recommender.import_utils import import_lightfm_silently


class RecommendationEngine(ABC):
    @abstractmethod
    def train(self, ratings):
        raise NotImplementedError

    @abstractmethod
    def recommend(self, ratings):
        raise NotImplementedError


@beartype
class LightFMEngine(RecommendationEngine):
    def __init__(self, movie_ids: list[str], model_file: Path) -> None:
        self.movie_ids = movie_ids
        self.db = connect_to_mongo()
        with open(model_file, "rb") as f:
            import_lightfm_silently()
            self.model = pickle.load(f)

    def get_movie_id(self, title: str) -> str:
        movies = self.db["movies"]
        movie = movies.find_one({"title": title})
        assert movie, title
        return f"{movie.get('netflix_id')}"

    def get_movie_title(self, netflix_id: str) -> str:
        movies = self.db["movies"]
        movie = movies.find_one({"netflix_id": f"{netflix_id}"})
        if movie:
            return f"{movie.get('title')}"
        else:
            return f"no title for {netflix_id=}"

    def titles_to_ids(self, titles: list[str]) -> list[str]:
        netflix_ids = []
        for title in titles:
            netflix_id = self.get_movie_id(title)
            netflix_ids.append(netflix_id)
        return netflix_ids

    def ids_to_titles(self, netflix_ids: list[str]) -> list[str]:
        titles = []
        for netflix_id in netflix_ids:
            title = self.get_movie_title(netflix_id)
            titles.append(title)
        return titles

    def get_recommendations(
        self,
        user_id: int,
        user_interactions: coo_matrix,
    ) -> NDArray[np.int_]:
        scores = self.model.predict(
            user_ids=user_id,
            item_ids=self.movie_ids,
            user_features=user_interactions,
        )
        return np.argsort(-scores)

    def get_data(self) -> list[str]:
        print("Enter liked movies: ")
        return input().split(",")

    def display_recommendations(self, recommendations: list[str]) -> None:
        movie_titles = self.ids_to_titles(recommendations)
        print("Recommended movies: ")
        for title in movie_titles:
            print(title)

    def create_user_matrix(self, liked_movies_ids: list[int]) -> coo_matrix:
        rows = [0] * len(liked_movies_ids)
        cols = liked_movies_ids
        data = [1] * len(liked_movies_ids)
        return coo_matrix((data, (rows, cols)))

    def recommend(self, user_id: int, limit: int = 10) -> set[int]:
        liked_movies = self.get_data()
        liked_movies_ids = list(map(int, self.titles_to_ids(liked_movies)))
        user_interactions = self.create_user_matrix(liked_movies_ids)
        print(f"{user_interactions=}")
        print(f"{user_interactions.shape=}")

        recommendations = self.get_recommendations(
            user_id, user_interactions)[:limit]
        return set(map(int, recommendations))
