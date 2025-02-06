"""
Recommends movies based on sparse input: the "cold start" problem.
"""

from warnings import filterwarnings

import numpy as np
from scipy.sparse import coo_matrix, dok_matrix
from sqlalchemy import text

from mediabridge.db.tables import get_engine


def recommend(
    max_training_user_id: int = 2_000,
) -> None:
    message = "LightFM was compiled without OpenMP support"
    filterwarnings("ignore", message, category=UserWarning)
    from lightfm import LightFM

    model = LightFM(no_components=30)
    train = _get_ratings(max_training_user_id)
    model.fit(train, epochs=10, num_threads=4)

    test_user_ids, test_movie_ids = _get_test_data(max_training_user_id)

    predictions = model.predict(test_user_ids, test_movie_ids)
    print(predictions)


def _get_ratings(
    max_user_id: int,
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
    return coo_matrix(matrix)


def _get_max_movie_id() -> int:
    # Movie IDs are VARCHARs in the database, which complicates matters.
    # That magic number of 4 is a pretty terrible to return 17_770 instead of 9999.
    query = "SELECT MAX(id)  FROM movie_title  WHERE LENGTH(id) > 4"
    with get_engine().connect() as conn:
        val = conn.execute(text(query)).scalar()
        return int(val or 0)


def _get_test_data(cutoff_user_id: int) -> tuple[list[int], list[int]]:
    query = "SELECT DISTINCT user_id  FROM rating  WHERE user_id > :cutoff_user_id  ORDER BY user_id"
    params = {"cutoff_user_id": cutoff_user_id}
    with get_engine().connect() as conn:
        test_user_ids = [u for u, in conn.execute(text(query), params)]
        query = "SELECT DISTINCT id  FROM movie_title"
        test_movie_ids = [int(m) for m, in conn.execute(text(query))]
        return test_user_ids[:17_770], sorted(test_movie_ids)
