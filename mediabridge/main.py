from data_processing.wiki_to_netflix import process_data, insert_into_mongo

#q = wiki_to_netflix.format_sparql_query('The Room', 2003)
#print(q)

if __name__ == '__main__':
    test = len(sys.argv) < 2 or sys.argv[1] != '--prod'
    data = process_data(test = test)
    insert_into_mongo(data)
