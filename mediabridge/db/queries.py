from typing import Any

from pymongo.database import Database
from pymongo.operations import InsertOne, UpdateOne

from mediabridge.db.connect import connect_to_mongo

MovieDoc = dict[str, str | int]


def insert_into_mongo(movie: list[str | int]) -> None:
    db = connect_to_mongo()
    collection = db["movies"]
    collection.update_one(
        {"_id": movie[1]},
        {
            "$set": {
                "netflix_id": movie[0],
                "wikidata_id": movie[1],
                "title": movie[2],
                "year": movie[3],
                "genre": movie[4],
                "director": movie[5],
            }
        },
        upsert=True,
    )


def bulk_insert(operations: list[UpdateOne | InsertOne[MovieDoc]]) -> None:
    db: Database[Any] = connect_to_mongo()
    collection = db["movies"]
    collection.bulk_write(operations)
