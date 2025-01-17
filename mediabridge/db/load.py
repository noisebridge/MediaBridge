from typer import Typer

app = Typer()


@app.command()
def load():
    """
    Load a csv of movie data into the mongo database.
    """
    pass

    # db = connect_to_mongo()
    # collection = db["movies"]
    # operations = []
    # with open("movies.csv", "r") as f:
    #     r = csv.reader(f)
    #     header = next(r)

    #     # operations.append(UpdateOne)


if __name__ == "__main__":
    app()
