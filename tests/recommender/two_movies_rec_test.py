import unittest
from time import time
from warnings import catch_warnings, filterwarnings

import pandas as pd

from mediabridge.db.tables import create_tables
from mediabridge.definitions import FULL_TITLES_TXT
from mediabridge.recommender.two_movies_rec import etl


class TestTwoMoviesRec(unittest.TestCase):
    def test_two_movies_rec(self) -> None:
        with catch_warnings():
            message = "LightFM was compiled without OpenMP support"
            filterwarnings("ignore", message, category=UserWarning)
            from lightfm import LightFM

            assert LightFM(loss="warp")
            create_tables()
            if FULL_TITLES_TXT.exists():
                t0 = time()
                etl()
                print(f"ETL finished in {time()-t0:.3f} s")

    def test_df(self) -> None:
        df = pd.DataFrame()
        assert df.empty
