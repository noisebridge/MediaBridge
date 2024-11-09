from mediabridge.data_processing import wiki_to_netflix

q = wiki_to_netflix.format_sparql_query("The Room", 2003)
print(q)
