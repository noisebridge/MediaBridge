"""
Recommends movies based on sparse input: the "cold start" problem.
"""

from warnings import filterwarnings

import numpy as np
from scipy.sparse import coo_matrix, dok_matrix
from sqlalchemy import text
from sqlalchemy.orm import Session

from mediabridge.db.tables import MovieTitle, get_engine


def recommend(
    max_training_user_id: int = 800,
    large_movie_id: int = 9_770,
) -> None:
    message = "LightFM was compiled without OpenMP support"
    filterwarnings("ignore", message, category=UserWarning)
    from lightfm import LightFM

    model = LightFM(no_components=30)
    train = _get_ratings(max_training_user_id, large_movie_id)
    model.fit(train, epochs=10, num_threads=4)

    test_movie_ids = _get_test_movie_ids(large_movie_id)

    # NB: predicting is very very non-deterministic. Each run _will_ produce different results.
    predictions = model.predict(max_training_user_id, test_movie_ids)
    assert isinstance(predictions, np.ndarray)
    assert predictions.shape == (len(test_movie_ids),)  # (8000, )
    mx = round(predictions.max(), 5)
    assert 0.0016 < mx < 0.0022, mx
    thresh = 0.85 * mx  # admit some more recommendations
    for i, p in enumerate(predictions):
        if p > thresh:
            netflix_id = test_movie_ids[i]  # map from internal to external ID
            print(i, "  ", netflix_id, "\t", p, "\t", _get_title(netflix_id))


def _get_ratings(
    max_user_id: int,
    large_movie_id: int,
    threshold: int = 4,
) -> coo_matrix:
    """Produces a sparse training matrix of just "positive" user ratings.

    We do not yet return any "negative" -1 values, e.g. for two- and one- star reviews.
    """
    query = """
    SELECT
        user_id,
        CAST(movie_id AS INTEGER)
    FROM rating
    WHERE
        user_id <= :max_user_id
        AND rating >= :threshold
    ORDER BY user_id, movie_id
    """
    params = {
        "max_user_id": max_user_id,
        "threshold": threshold,
    }
    matrix = dok_matrix(
        (max_user_id + 1, _get_max_movie_id() + 1),
        dtype=np.int8,
    )
    with get_engine().connect() as conn:
        for u, m in conn.execute(text(query), params):
            matrix[u, m] = 1

            # Blind the model to the movies we want to predict.
            if u == max_user_id and m >= large_movie_id:
                matrix[u, m] = 0
                del matrix[u, m]
                print(u, m)

    return coo_matrix(matrix)


def _get_max_movie_id() -> int:
    # Movie IDs are VARCHARs in the database, which complicates matters.
    # That horrible magic number of 4 lets us return 17_770 instead of 9999.
    query = "SELECT MAX(id)  FROM movie_title  WHERE LENGTH(id) > 4"
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


def _get_title(netflix_id: int) -> str:
    with Session(get_engine()) as sess:
        movie = sess.query(MovieTitle).filter(MovieTitle.id == netflix_id).first()
        return str(movie.title)
