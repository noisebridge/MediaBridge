import pickle

import numpy as np
from scipy import sparse

from mediabridge.db.connect import connect_to_mongo


class RecommendationEngine:
    def __init__(self, movie_ids, model_file):
        self.movie_ids = movie_ids
        self.db = connect_to_mongo()
        with open(model_file, "rb") as f:
            self.model = pickle.load(f)

    def get_movie_id(self, title):
        movies = self.db["movies"]
        return movies.find_one({"title": title}).get("netflix_id")

    def get_movie_title(self, netflix_id):
        movies = self.db["movies"]
        return movies.find_one({"netflix_id": netflix_id}).get("title")

    def titles_to_ids(self, titles):
        netflix_ids = []
        for title in titles:
            netflix_id = self.get_movie_id(title)
            titles.append(netflix_id)
        return netflix_ids

    def ids_to_titles(self, netflix_ids):
        titles = []
        for netflix_id in netflix_ids:
            title = self.get_movie_title(netflix_id)
            titles.append(title)
        return titles

    def get_recommendations(self, user_id, user_interactions):
        scores = self.model.predict(
            user_ids=user_id,
            item_ids=self.movie_ids,
            user_features=user_interactions,
        )
        return np.argsort(-scores)

    def get_data(self):
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

    def recommend(self, user_id=0):
        liked_movies = self.get_data()
        liked_movies_ids = self.titles_to_ids(liked_movies)
        user_interactions = self.create_user_matrix(liked_movies_ids)

        recommendations = self.get_recommendations(user_id, user_interactions)
        self.display_recommendations(recommendations[:10])
