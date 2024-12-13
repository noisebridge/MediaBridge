from mediabridge.db.connect import connect_to_mongo


def insert_into_mongo(movie):
    db = connect_to_mongo()
    collection = db["movies"]
    collection.update_one(
        {"wikidata_id": movie[1]},
        {
            "set": {
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
