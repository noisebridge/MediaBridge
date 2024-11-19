import sys

from mediabridge.db.connect import insert_into_mongo
from mediabridge.db.insert_data import process_data

# q = wiki_to_netflix.format_sparql_query('The Room', 2003)
# print(q)

if __name__ == '__main__':
    test = len(sys.argv) < 2 or sys.argv[1] != '--prod'
    data = process_data(test=test)
    insert_into_mongo(data)
