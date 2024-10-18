from wiki_to_netflix import format_sparql_query, wiki_query, process_data
from wiki_to_netflix_test_data import EXPECTED_SPARQL_QUERY

def test_format_sparql_query():
    QUERY = format_sparql_query("The Room", 2003)
    assert QUERY == EXPECTED_SPARQL_QUERY