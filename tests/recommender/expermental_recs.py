import random
import unittest

from sqlalchemy.orm import sessionmaker

from mediabridge.data_processing.etl import etl
from mediabridge.db.tables import MovieTitle, Rating, create_tables, get_engine
from mediabridge.definitions import FULL_TITLES_TXT
from mediabridge.recommender.make_recommendation import recommend

"""
Things I want to do:

Filter a users rating to "bind" the model, starting at the year 2000.
    *I need to pick a users, remove movies that are released after the year 2000   

Running this file:
    first you need to make sure movie_titles.txt is in the data folder
    that this file https://github.com/deesethu/Netflix-Dataset.git is cloned to the parent directory of the project

    then run the commmand:
    PYTHONPATH=$(pwd) pipenv run python tests/recommender/expermental_recs.py

Things to ask about:
    i don't know if the test two movies rec actually does anything

"""


def get_random_user():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query to get all user IDs
    user_ids = session.query(Rating.user_id).distinct().all()
    user_ids = [user_id[0] for user_id in user_ids]  # Extract user IDs from tuples

    # Pick a random user ID
    random_user_id = random.choice(user_ids)

    session.close()
    return random_user_id


def get_user_ratings(user_id):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query to get ratings + movie title + release year
    user_ratings = (
        session.query(Rating.movie_id, Rating.rating, MovieTitle.title, MovieTitle.year)
        .join(MovieTitle, Rating.movie_id == MovieTitle.id)
        .filter(Rating.user_id == user_id)
        .all()
    )

    session.close()
    return user_ratings


def get_movie_details(movie_ids):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    movie_details = (
        session.query(MovieTitle.id, MovieTitle.title, MovieTitle.year)
        .filter(MovieTitle.id.in_(movie_ids))
        .all()
    )

    session.close()
    return movie_details


if __name__ == "__main__":
    create_tables()
    etl(1000000)

    # Get a random user ID
    random_user_id = get_random_user()
    # random_user_id = 2000

    # Fetch user ratings
    user_ratings = get_user_ratings(random_user_id)

    print(f"Random User ID: {random_user_id}\n")
    for movie_id, rating, title, year in user_ratings:
        print(f"Title: {title} ({year}), Rating: {rating}")

    # Get recommended movies
    recommended_movie_ids = recommend(max_training_user_id=random_user_id)

    # Convert movie IDs to titles
    recommended_movies = get_movie_details(recommended_movie_ids)

    print(f"\nRecommended Movies for User {random_user_id}:")
    for movie_id, title, year in recommended_movies:
        print(f"Title: {title} ({year})")
