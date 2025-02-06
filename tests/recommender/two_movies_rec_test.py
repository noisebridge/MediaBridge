import unittest
from time import time
from warnings import catch_warnings, filterwarnings

import pandas as pd

from mediabridge.db.tables import create_tables
from mediabridge.definitions import FULL_TITLES_TXT
from mediabridge.recommender.etl import etl


class TestTwoMoviesRec(unittest.TestCase):
    def test_etl(self) -> None:
        with catch_warnings():
            message = "LightFM was compiled without OpenMP support"
            filterwarnings("ignore", message, category=UserWarning)
            from lightfm import LightFM

            assert LightFM(loss="warp")
            create_tables()
            if FULL_TITLES_TXT.exists():
                # A million rows corresponds to a four-second ETL.
                t0 = time()
                etl("mv_00*.txt", max_rows=1_000_000)
                print(f"ETL finished in {time() - t0:.3f} s")

   