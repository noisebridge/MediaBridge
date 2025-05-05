from typing import Any

import flask
import typer
from flask_cors import CORS
from sqlalchemy import text

from mediabridge.db.tables import get_engine

typer_app = typer.Typer()


app = flask.Flask(__name__)
CORS(app)


@app.route("/")  # type: ignore
def hello_world() -> str:
    return "MediaBridge API is running!"


@app.route("/api/v1/movie/search")  # type: ignore
def search_movies() -> tuple[Any, int]:
    query = flask.request.args.get("q")
    if not query:
        return flask.jsonify({"error": "Query parameter 'q' is required."}), 400

    with get_engine().connect() as conn:
        pattern = f"%{query}%"
        movies = conn.execute(
            text(
                "SELECT * FROM movie_title WHERE LOWER(title) LIKE LOWER(:pattern) LIMIT 10"
            ),
            {"pattern": pattern},
        ).fetchall()
        movies_list = [row._asdict() for row in movies]
        return flask.jsonify(movies_list)


@typer_app.command()
def serve(ctx: typer.Context, debug: bool = True) -> None:
    """
    Serve the Flask app.
    """
    app.run(debug=debug)
