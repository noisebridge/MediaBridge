import pickle

import numpy as np


class RecommendationEngine:
    def __init__(self, model_file):
        with open(model_file, "rb") as f:
            self.model = pickle.load(f)

    def titles_to_ids(self, titles):
        pass

    def ids_to_titles(self, ids):
        pass

    def get_recommendations(self, user_id, movie_ids):
        scores = self.model.predict(
            user_id,
            movie_ids,
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

    def recommend(self, user_id=1):
        liked_movies = self.get_data(user_id)
        liked_movies_ids = self.titles_to_ids(liked_movies)
        recommendations = self.get_recommendations(user_id, liked_movies_ids)
        self.display_recommendations(recommendations)
