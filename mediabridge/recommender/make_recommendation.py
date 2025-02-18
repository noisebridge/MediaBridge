"""
Recommends movies based on sparse input: the "cold start" problem.

This is a WIP, a work in progress.
It demonstrates the bare minimum to exercise the LightFM library.

Several design decisions should definitely be revisited:
(1.) There are "training" users that offer the model complete information,
     and "test" users that offer a handful of rated movies and then
     we need to predict the rest.
     Currently there's a single test user, and the distinction between "revealed"
     and "hidden" movies for that user comes from an integer ID comparison
     against large_movie_id.
     We of course wish for the model to support multiple test users.
     And hoping that numeric movie IDs have e.g. random genre as opposed to
     being sorted by genre is not a solid assumption. Similarly for popularity or year.
     So we need a better way of identifying the hidden movies that the model
     should be blinded to during initial training.
(2.) DONE: represent one-star ratings as -1.
(3.) We are not yet taking advantage of optional parameters that would let us tell
     the model about user demographics or movie genre information.
     Note that demographics could include variables like age and gender,
     but it could also include details available in the dataset, like "I am a prolific rater",
     "I love sci-fi", or "I hate horror".
(4.) Maybe initial ETL should be run by "pipenv run dev etl"?
     Or maybe we run that automatically as needed, and "pipenv run dev recommend"
     is the user interface that should be added to the code base?
     Perhaps with parameters that describe users or movies of interest?

You can view the test output with:
$ pipenv run python -m unittest tests/*/*_test.py
"""

from warnings import filterwarnings

import numpy as np
from scipy.sparse import coo_matrix, dok_matrix
from sqlalchemy import text
from sqlalchemy.orm import Session

from mediabridge.db.tables import MovieTitle, get_engine


def recommend(
    max_training_user_id: int = 798,
    large_movie_id: int = 9_770,
) -> set[int]:
    """Recommends a set of movies, by netflix_id, for a given user.

    The subject user is identified by max_training_user_id.
    Lower IDs reveal full ratings information to the model.
    Larger IDs are completely ignored, leading to quicker test runs.

    For the subject user we reveal only a subset of movie preferences.
    Movie IDs below large_movie_id are revealed to the model during training,
    while larger IDs are hidden and are fair game to possibly recommend to the user.
    Clearly there is room to improve on this crude method of splitting into subsets.
    """
    message = "LightFM was compiled without OpenMP support"
    filterwarnings("ignore", message, category=UserWarning)
    from lightfm import LightFM

    model = LightFM(no_components=30)
    train = _get_ratings(max_training_user_id, large_movie_id)
    model.fit(train, epochs=10, num_threads=4)

    test_movie_ids = _get_test_movie_ids(large_movie_id)

    predictions = model.predict(max_training_user_id, test_movie_ids)
    assert isinstance(predictions, np.ndarray)
    assert predictions.shape == (len(test_movie_ids),)  # (8000, )
    mx = round(predictions.max(), 5)
    thresh = 0.91 * mx  # admit some more recommendations, not just the top one
    # netflix_id = test_movie_ids[i]  # maps from internal to external netflix ID

    return {test_movie_ids[i] for i, p in enumerate(predictions) if p > thresh}


def _normalize_rating(rating: int) -> float:
    """Maps a star rating to the interval [-1, 1], for a logistic loss model."""
    # The inputs skew toward positive ratings, so the overall mean will be positive.
    # We may need to defer normalization until the sample mean is known.
    assert 1 <= rating <= 5
    return (rating - 3) / 2


def _get_ratings(
    max_user_id: int,
    large_movie_id: int,
) -> coo_matrix:
    """Produces a sparse training matrix of thumbs {up, down} user ratings.

    We ignore "neutral" three-star ratings.
    """
    query = """
    SELECT
        user_id,
        CAST(movie_id AS INTEGER),
        rating
    FROM rating
    WHERE
        user_id <= :max_user_id
        AND rating != 3
    ORDER BY user_id, movie_id
    """
    params = {
        "max_user_id": max_user_id,
    }
    matrix = dok_matrix(
        (max_user_id + 1, _get_max_movie_id() + 1),
        dtype=np.int8,
    )
    with get_engine().connect() as conn:
        for u, m, r in conn.execute(text(query), params):
            matrix[u, m] = _normalize_rating(r)

            # Blind the model to the movies we want to predict.
            if u == max_user_id and m >= large_movie_id:
                matrix[u, m] = 0

    return coo_matrix(matrix)


def _get_max_movie_id() -> int:
    # Movie IDs are VARCHARs in the database, which complicates matters.
    # Sorting by length and then lexically lets us return 17_770 instead of 9_999.
    query = "SELECT id  FROM movie_title  ORDER BY LENGTH(id) DESC, id DESC  LIMIT 1"
    with get_engine().connect() as conn:
        val = conn.execute(text(query)).scalar()
        return int(val or 0)


def _get_test_movie_ids(
    large_movie_id: int,
) -> list[int]:
    query = """
    SELECT id
    FROM movie_title
    WHERE CAST(id AS INTEGER) > :max_training_user_id
    """
    params = {"max_training_user_id": large_movie_id}
    with get_engine().connect() as conn:
        test_movie_ids = [int(m) for m, in conn.execute(text(query), params)]
        return sorted(test_movie_ids)


def get_title(netflix_id: int) -> str:
    with Session(get_engine()) as sess:
        movie = sess.get(MovieTitle, netflix_id)
        assert movie, netflix_id
        return str(movie.title)
