import pickle

import numpy as np
from scipy import sparse


class RecommendationEngine:
    def __init__(self, data, model_file):
        self.data = data
        with open(model_file, "rb") as f:
            self.model = pickle.load(f)

    def titles_to_ids(self, titles):
        pass

    def ids_to_titles(self, ids):
        pass

    def get_recommendations(self, user_id, user_interactions):
        scores = self.model.predict(
            user_ids=0,
            item_ids=self.data,
            user_features=user_interactions,
        )
        return np.argsort(-scores)

    def get_data(self, user_id):
        print("Enter liked movies: ")
        return input().split(",")

    def display_recommendations(self, recommendations):
        movie_titles = self.ids_to_titles(recommendations)
        print("Recommended movies: ")
        for title in movie_titles:
            print(title)

    def create_user_matrix(self, liked_movies_ids):
        rows = [0] * len(liked_movies_ids)
        cols = liked_movies_ids
        data = [1] * len(liked_movies_ids)
        return sparse.coo_matrix((data, (rows, cols)))

    def recommend(self, user_id=1):
        liked_movies = self.get_data(user_id)
        liked_movies_ids = self.titles_to_ids(liked_movies)
        user_interactions = self.create_user_matrix(liked_movies_ids)

        recommendations = self.get_recommendations(user_id, user_interactions)
        self.display_recommendations(recommendations[:10])
