from src.data_processing.wiki_to_netflix import format_sparql_query, wiki_query, process_data
from . import constants

def test_format_sparql_query():
    QUERY = format_sparql_query("The Room", 2003)
    assert QUERY == constants.SPARQL_QUERY