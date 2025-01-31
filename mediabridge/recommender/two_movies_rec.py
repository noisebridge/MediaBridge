"""
Recommends movies based on sparse input: the "cold start" problem.
"""

import numpy as np
import pandas as pd

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.definitions import FULL_TITLES_TXT


def etl() -> None:
    df = pd.DataFrame(
        read_netflix_txt(FULL_TITLES_TXT), columns=["id", "year", "title"]
    )
    df["year"] = df.year.replace("NULL", pd.NA).astype("Int16")
    print(df)
