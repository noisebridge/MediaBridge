import unittest
from logging import getLogger
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from typer import Context

import mediabridge.data_processing.wiki_to_netflix as w_to_n
from mediabridge.data_processing.wiki_to_netflix_test_data import (
    EXPECTED_SPARQL_QUERY,
    WIKIDATA_RESPONSE_THE_ROOM,
)
from mediabridge.definitions import DATA_DIR, FULL_TITLES_TXT, PROJECT_DIR
from mediabridge.schemas.movies import EnrichedMovieData, MovieData
from tests.logging_util import silence_logging

TITLES_TXT = PROJECT_DIR / "tests/test-data/movie_titles_test.txt"
TITLES_CSV = TITLES_TXT.with_suffix(".csv")


class TestWikiToNetflix(unittest.TestCase):
    def test_format_sparql_query(self) -> None:
        QUERY = w_to_n.format_sparql_query("The Room", 2003)
        assert QUERY == EXPECTED_SPARQL_QUERY

    @patch("mediabridge.data_processing.wiki_to_netflix.requests")
    def test_wiki_query(self, mock_requests: MagicMock) -> None:
        mock_requests.post.return_value.json.return_value = WIKIDATA_RESPONSE_THE_ROOM
        movie = MovieData("0", "The Room", 2003)
        result = w_to_n.wiki_query(movie)
        assert result

        # Order of genres is not guaranteed, so we sort before checking for equality
        result.genres.sort()

        self.assertEqual(
            result,
            EnrichedMovieData(
                netflix_id="0",
                title="The Room",
                year=2003,
                wikidata_id="Q533383",
                genres=["drama film", "independent film", "romance film"],
                director="Tommy Wiseau",
            ),
        )

    def test_wiki_query_not_found(self) -> None:
        """This integration test simply provokes the "whoops, no match" case in the target code."""

        log = getLogger("mediabridge.data_processing.wiki_to_netflix")
        with silence_logging(log):
            assert w_to_n.wiki_query(MovieData("-1", "No Such Movie", 1901)) is None

    def test_read_netflix_txt(self) -> None:
        movies = list(w_to_n.read_netflix_txt(TITLES_TXT, 3))
        assert len(movies) == 3
        assert movies[-1] == ["3", "1997", "Character"]

        # Sometimes we're in an environment, like CI, where we never downloaded the full dataset.
        # So silently succeed, without attempting to read thousands of non-existent entries.
        if FULL_TITLES_TXT.exists():
            movies = list(w_to_n.read_netflix_txt(FULL_TITLES_TXT))
            assert len(movies) == 17_770
            assert movies[-1] == ["17770", "2003", "Alien Hunter"]

    def test_create_netflix_csv(self) -> None:
        output_csv = DATA_DIR / "movie_titles.csv"
        few_rows = 3  # A conveniently small number of rows, for fast tests.
        rows = list(w_to_n.read_netflix_txt(TITLES_TXT, few_rows))
        movies = [MovieData(id, title, int(year)) for id, year, title in rows]

        w_to_n.create_netflix_csv(output_csv, movies)
        lines = output_csv.read_text().splitlines()

        assert len(lines) == few_rows + 1
        assert lines[-1] == "3,Character,1997"

    def test_wiki_feature_info(self) -> None:
        # This is a silly test, designed to provoke `return None`,
        # something that live wikidata results is never observed to do.
        # (Don't believe me? Put an `assert False` in that function and see if it triggers.)
        # Recommend deleting this test, and the target code clause it is written for.
        no_entries: list[str] = []
        data = {"results": {"bindings": no_entries}}
        assert w_to_n.wiki_feature_info(data, "clavis") is None

    def _process_with_path_missing(self, actual: Path) -> None:
        """Verifies we get an error from process_data(), when a path is momentarily missing."""
        ephemeral = Path(f"{actual}-missing")
        assert not ephemeral.exists()
        actual.rename(ephemeral)
        try:
            with self.assertRaises(FileNotFoundError):
                w_to_n.process_data(TITLES_TXT, 1, None)
        finally:
            ephemeral.rename(actual)

    def test_process_data_pretend_theres_no_data_dir(self) -> None:
        TITLES_CSV.unlink(missing_ok=True)

        self._process_with_path_missing(TITLES_TXT.parent)
        self._process_with_path_missing(TITLES_TXT)

        assert not TITLES_CSV.exists()

    def test_process(self) -> None:
        ctx = Context(command=example_command, info_name="mediabridge")
        csv = FULL_TITLES_TXT.with_suffix(".csv")

        if FULL_TITLES_TXT.exists():
            # At this point we're on a developer's laptop, rather than in CI.
            csv.unlink(missing_ok=True)

            w_to_n.process(ctx, 2, csv, full=False)

        self.assertGreaterEqual(csv.stat().st_size, 82)
        ctx.invoke(example_command)


@click.command()
def example_command() -> None:
    """This no-op lets us build a well-formed Context."""
