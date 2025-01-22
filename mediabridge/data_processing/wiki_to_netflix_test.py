import unittest

import mediabridge.data_processing.wiki_to_netflix as w_to_n
from mediabridge.data_processing.wiki_to_netflix_test_data import EXPECTED_SPARQL_QUERY
from mediabridge.definitions import DATA_DIR
from mediabridge.schemas.movies import EnrichedMovieData, MovieData


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

    def test_read_netflix_txt(self) -> None:
        titles_txt = DATA_DIR / "movie_titles.txt"

        movies = list(w_to_n.read_netflix_txt(titles_txt))
        assert len(movies) == 17_770
        assert movies[-1] == ["17770", "2003", "Alien Hunter"]

        movies = list(w_to_n.read_netflix_txt(titles_txt, 3))
        assert len(movies) == 3
        assert movies[-1] == ["3", "1997", "Character"]
