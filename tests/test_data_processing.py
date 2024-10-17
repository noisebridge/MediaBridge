from src.data_processing.wiki_to_netflix import format_sparql_query, wiki_query, process_data

def test_process_data():
    process_data(test=True)