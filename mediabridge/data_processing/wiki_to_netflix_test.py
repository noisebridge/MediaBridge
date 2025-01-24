import logging
import unittest
from contextlib import contextmanager
from logging import Logger
from pathlib import Path

import mediabridge.data_processing.wiki_to_netflix as w_to_n
from mediabridge.data_processing.wiki_to_netflix_test_data import EXPECTED_SPARQL_QUERY
from mediabridge.definitions import DATA_DIR
from mediabridge.schemas.movies import EnrichedMovieData, MovieData

TITLES_TXT = DATA_DIR / "movie_titles.txt"


def silence_logging(self, logger: Logger):
    """A helper context manager to suppress logs from cluttering test output."""

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass  # Ignore all log records

    @contextmanager
    def _silence_logging():
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()
        logger.addHandler(NullHandler())

        try:
            yield  # Let the test code run for a bit.
        finally:
            logger.handlers = original_handlers  # Turn logging back on.

    # Return the context manager
    return _silence_logging()


class TestWikiToNetflix(unittest.TestCase):
    def test_format_sparql_query(self) -> None:
        QUERY = w_to_n.format_sparql_query("The Room", 2003)
        assert QUERY == EXPECTED_SPARQL_QUERY

    def test_wiki_query(self) -> None:
        # Integration test -- this hits the wikidata.org webserver.
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

        # We need a better story about "real" or "mock" data in CI. Currently, there just isn't any.

        log = logging.getLogger("mediabridge.data_processing.wiki_to_netflix")
        with silence_logging(self, log):
            assert w_to_n.wiki_query(MovieData("-1", "No Such Movie", 1901)) is None

    def test_read_netflix_txt(self) -> None:
        movies = list(w_to_n.read_netflix_txt(TITLES_TXT))
        assert len(movies) == 17_770
        assert movies[-1] == ["17770", "2003", "Alien Hunter"]

        movies = list(w_to_n.read_netflix_txt(TITLES_TXT, 3))
        assert len(movies) == 3
        assert movies[-1] == ["3", "1997", "Character"]

        # w_to_n.process_data(3, TITLES_TXT)

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
        """Verifies we get an error from process_data(), when a path is momentarily is missing."""
        ephemeral = Path(f"{actual}-missing")
        assert actual.exists()
        actual.rename(ephemeral)
        try:
            with self.assertRaises(FileNotFoundError):
                w_to_n.process_data(1, None)
        finally:
            ephemeral.rename(actual)

    def test_process_data_pretend_theres_no_data_dir(self) -> None:

        self._process_with_path_missing(DATA_DIR)
        self._process_with_path_missing(TITLES_TXT)

    def test_process_data(self) -> None:
        pass
