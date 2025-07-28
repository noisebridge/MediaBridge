import pickle

import numpy as np
import typer
from scipy.sparse import coo_matrix, dok_matrix
from sqlalchemy import text
from tqdm import tqdm

from mediabridge.db.tables import get_engine
from mediabridge.definitions import OUTPUT_DIR
from mediabridge.recommender.make_recommendation import normalize_rating

MAX_USER_ID = 2_649_429
NUM_MOVIES = 17_770

app = typer.Typer()


def create_matrix(max_user_id: int) -> coo_matrix:
    query = f"""
    SELECT
        user_id,
        CAST(movie_id AS INTEGER),
        rating
    FROM rating
    WHERE rating != 3
      AND user_id <= {max_user_id}
    ORDER BY user_id DESC
    """

    matrix = dok_matrix(
        (MAX_USER_ID + 1, NUM_MOVIES + 1),
        dtype=np.int8,
    )
    with get_engine().connect() as conn:
        for u, m, r in tqdm(conn.execute(text(query)), total=71669260):
            matrix[u, m] = normalize_rating(r)

    m = matrix.tocoo()
    assert isinstance(m, coo_matrix)
    return m


FINAL_USER = 2_649_375


@app.command()
def save_matrix(
    ctx: typer.Context,
    max_user_id: int = FINAL_USER,
    *,
    debug: bool = True,
) -> None:
    """Create and save the interaction matrix from the user."""
    fname = "interaction_matrix.pkl"
    if max_user_id < FINAL_USER:
        fname = f"short_{fname}"
    output_file = OUTPUT_DIR / fname
    output_file.parent.mkdir(exist_ok=True)

    matrix = create_matrix(max_user_id)
    with open(output_file, "wb") as f:
        pickle.dump(matrix, f)
    print(f"Interaction matrix saved to {output_file}")
