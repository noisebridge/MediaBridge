import unittest
from warnings import catch_warnings, filterwarnings

import pandas as pd

from mediabridge.recommender.two_movies_rec import etl


class TestTwoMoviesRec(unittest.TestCase):
    def test_two_movies_rec(self) -> None:
        with catch_warnings():
            message = "LightFM was compiled without OpenMP support"
            filterwarnings("ignore", message, category=UserWarning)
            from lightfm import LightFM

            assert LightFM(loss="warp")
            etl()

    def test_df(self) -> None:
        df = pd.DataFrame()
        assert df.empty
