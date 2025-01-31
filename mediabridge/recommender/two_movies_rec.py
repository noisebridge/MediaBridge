"""
Recommends movies based on sparse input: the "cold start" problem.
"""

import pandas as pd

from mediabridge.data_processing.wiki_to_netflix import read_netflix_txt
from mediabridge.definitions import FULL_TITLES_TXT


def etl() -> None:
    netflix_df = pd.DataFrame(read_netflix_txt(FULL_TITLES_TXT))
    print(netflix_df)
