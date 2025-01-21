from mediabridge.schemas.movies import EnrichedMovieData


def test_flatten_values():
    vals = EnrichedMovieData(
        1, "The Matrix", 1999, "Q11424", ["Action", "Drama"], "Lana Wachowski"
    ).flatten_values()
    assert vals == {
        "netflix_id": "1",
        "wikidata_id": "Q11424",
        "title": "The Matrix",
        "year": "1999",
        "genres": "Action;Drama",
        "director": "Lana Wachowski",
    }
