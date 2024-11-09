from wiki_to_netflix import format_sparql_query
from wiki_to_netflix_test_data import EXPECTED_SPARQL_QUERY


def test_format_sparql_query():
    QUERY = format_sparql_query("The Room", 2003)
    assert QUERY == EXPECTED_SPARQL_QUERY


def get_example_json_sparql_response():
    """
    Returns an example response structure for testing.
    """
    return {
        "results": {
            "bindings": [
                {
                    "item": {
                        "type": "uri",
                        "value": "http://www.wikidata.org/entity/Q12345",
                    },
                    "genreLabel": {"type": "literal", "value": "Science Fiction"},
                    "directorLabel": {"type": "literal", "value": "John Doe"},
                }
            ]
        }
    }
