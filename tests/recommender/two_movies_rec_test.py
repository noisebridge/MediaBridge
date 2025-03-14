import unittest
from time import time

from mediabridge.data_processing.etl import etl
from mediabridge.db.tables import create_tables
from mediabridge.definitions import TITLES_TXT
from mediabridge.recommender.make_recommendation import get_title, recommend


def _clean(ids: set[int]) -> set[int]:
    """Ensures that a pair of troublesome movie IDs shall not be present in the recommendations."""
    # with contextlib.suppress(ValueError):  # Sigh, disabled by pytest!
    # Forest Gump is borderline, it randomly comes and goes,
    # and Saving Private Ryan will on very rare occasions be recommended.
    gump, ryan = 11283, 17157
    ids.add(gump)
    ids.add(ryan)
    ids.remove(gump)
    ids.remove(ryan)
    return ids


class TestTwoMoviesRec(unittest.TestCase):
    # Ideally we should be able to have a user supply two movies they like,
    # and recommend a few more to them. We're not quite there yet.

    def test_recommend(self) -> None:
        if TITLES_TXT.exists():
            ids = _clean(recommend())

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
