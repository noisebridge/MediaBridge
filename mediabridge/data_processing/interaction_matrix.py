import pickle
from pathlib import Path

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


def create_matrix() -> coo_matrix:
    query = """
    SELECT
        user_id,
        CAST(movie_id AS INTEGER),
        rating
    FROM rating
    WHERE rating != 3
    ORDER BY user_id DESC
    """

    matrix = dok_matrix(
        (MAX_USER_ID + 1, NUM_MOVIES + 1),
        dtype=np.float32,
    )
    with get_engine().connect() as conn:
        print("connected")
        for u, m, r in tqdm(conn.execute(text(query)), total=71669260):
            print(u, m, normalize_rating(r))
            matrix[u, m] = normalize_rating(r)

    m = matrix.tocoo()
    assert isinstance(m, coo_matrix)
    return m


@app.command()
def save_matrix(
    ctx: typer.Context,
    debug: bool = True,
    output_file: Path = OUTPUT_DIR / "interaction_matrix.pkl",
) -> None:
    """Create and save the interaction matrix from the user."""
    output_file.parent.mkdir(exist_ok=True)

    matrix = create_matrix()
    with open(output_file, "wb") as f:
        pickle.dump(matrix, f)
    print(f"Interaction matrix saved to {output_file}")
