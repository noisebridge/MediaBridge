from dotenv import load_dotenv
import os
import pymongo
from pymongo import MongoClient

load_dotenv()

def connect_to_mongo():
    db_username = os.getenv('mongodb_username')
    db_password = os.getenv('mongodb_password')
    mongo_url = os.getenv('mongodb_uri')
    client = MongoClient(mongo_url, username = db_username, password = db_password)
    db = client['mediabridge']
    collection = db["movies"]
    return collection

def insert_into_mongo(movie):
    get_collection = connect_to_mongo()
    get_collection.update_one({'wikidata_id': movie[1]}, 
        {'set': {
        'netflix_id': movie[0],
        'wikidata_id': movie[1],
        'title': movie[2],
        'year': movie[3],
        'genre': movie[4],
        'director': movie[5]} },
        upsert = True)
