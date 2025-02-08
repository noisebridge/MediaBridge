import unittest
from time import time

from mediabridge.data_processing.etl import etl
from mediabridge.db.tables import create_tables
from mediabridge.definitions import FULL_TITLES_TXT
from mediabridge.recommender.make_recommendation import get_title, recommend


class TestTwoMoviesRec(unittest.TestCase):
    # Ideally we should be able to have a user supply two movies they like,
    # and recommend a few more to them. We're not quite there yet.

    def test_etl(self) -> None:
        # We might choose another way to run the ETL, outside of a test framework.
        # The current code was enough to support an edit-run cycle during initial development.

        # For example, tests may run in arbitrary order, yet recommend() depends on ETL.
        # ETL effects persist across test runs, so a failed initial run will let later tests succeed.

        create_tables()
        if FULL_TITLES_TXT.exists():
            # A million rows corresponds to a four-second ETL.
            t0 = time()

            etl(max_rows=101_000_000)

            elapsed = time() - t0
            x = (elapsed < 10) or print(f"ETL finished in {elapsed:.3f} s")
            assert x in (True, None)  # we simply evaluated for side effects

    def test_recommend(self) -> None:
        if FULL_TITLES_TXT.exists():

            ids = recommend()

            # with contextlib.suppress(ValueError):  # Sigh, disabled by pytest!
            # Forest Gump is borderline; it randomly comes and goes.
            gump = 11283
            ids.add(gump)
            ids.remove(gump)
            self.assertEqual(
                {11521, 14550, 16377},
                ids,
            )
            self.assertEqual(
                """
Lord of the Rings: The Two Towers
The Shawshank Redemption: Special Edition
The Green Mile
""".strip(),
                "\n".join(map(get_title, sorted(ids))),
            )

        # Consider evaluating the result with
        # https://making.lyst.com/lightfm/docs/lightfm.evaluation.html#lightfm.evaluation.precision_at_k
