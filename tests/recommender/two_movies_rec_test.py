import unittest
from time import time
from warnings import catch_warnings, filterwarnings

from mediabridge.db.tables import create_tables
from mediabridge.definitions import FULL_TITLES_TXT
from mediabridge.recommender.etl import etl
from mediabridge.recommender.two_movies_rec import recommend


class TestTwoMoviesRec(unittest.TestCase):
    def setUp(self) -> None:
        with catch_warnings():
            message = "LightFM was compiled without OpenMP support"
            filterwarnings("ignore", message, category=UserWarning)
            from lightfm import LightFM

            assert LightFM(loss="warp")

    def test_etl(self) -> None:
        # We might choose another way to run the ETL, outside of a test framework.
        # The current code was enough to support an edit-run cycle during initial development.

        create_tables()
        if FULL_TITLES_TXT.exists():
            # A million rows corresponds to a four-second ETL.
            t0 = time()
            etl("mv_00*.txt", max_rows=1_000_000)
            elapsed = time() - t0
            x = (elapsed < 10) or print(f"ETL finished in {elapsed:.3f} s")
            assert x in (True, None)  # we simply evaluated for side effects

    def test_recommend(self) -> None:
        recommend()
