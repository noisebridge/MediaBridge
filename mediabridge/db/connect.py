import os
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()


def connect_to_mongo() -> Database[Any]:
    # This will raise an exception if MONGODB_URI is not defined in the environment.
    # If that isn't enough information to help developers populate their environment,
    # we should use `get` and throw a custom message if the value is missing.
    mongo_uri = os.environ["MONGODB_URI"]
    client: MongoClient[Any] = MongoClient(mongo_uri)
    db = client["mediabridge"]
    return db
