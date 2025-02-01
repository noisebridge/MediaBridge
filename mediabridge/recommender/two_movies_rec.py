"""
Recommends movies based on sparse input: the "cold start" problem.
"""

import numpy as np
import pandas as pd
from sqlalchemy.sql import text

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.db.tables import get_engine
from mediabridge.definitions import FULL_TITLES_TXT


def etl() -> None:
    columns = ["id", "year", "title"]
    df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT), columns=columns)
    df["year"] = df.year.replace("NULL", pd.NA).astype("Int16")
    print(df)

    with get_engine().connect() as connection:
        connection.execute(text("DELETE FROM movie_title"))
        df.to_sql("movie_title", connection, index=False, if_exists="append")
