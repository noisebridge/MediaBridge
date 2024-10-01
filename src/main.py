from data_processing.wiki_to_netflix import * 

if __name__ == '__main__':
    data = process_data(True)
    insert_into_mongo(data)
