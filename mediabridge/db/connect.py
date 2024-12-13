# MongoDB connection setup
import os
from functools import cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


@cache
def connect_to_mongo():
    # This will raise an exception if MONGODB_URI is not defined in the environment.
    # If that isn't enough information to help developers populate their environment,
    # we should use `get` and throw a custom message if the value is missing.
    mongo_uri = os.environ["MONGODB_URI"]
    client = MongoClient(mongo_uri)
    db = client["mediabridge"]
    return db
