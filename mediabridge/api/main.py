import typer
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from sqlalchemy import text

from mediabridge.db.tables import get_engine

typer_app = typer.Typer()


app = Flask(__name__)
CORS(app)


@app.route("/")  # type: ignore
def hello_world() -> str:
    return "MediaBridge API is running!"


@app.route("/api/v1/movie/search")  # type: ignore
def search_movies() -> tuple[Response, int]:
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    with get_engine().connect() as conn:
        select = "SELECT id, year, title FROM movie_title WHERE LOWER(title) LIKE LOWER(:pattern) LIMIT 10"
        pattern = f"%{query}%"
        movies = conn.execute(
            text(select),
            {"pattern": pattern},
        ).fetchall()
        movies_list = [row._asdict() for row in movies]
        return jsonify(movies_list), 200


@typer_app.command()
def serve(ctx: typer.Context, debug: bool = True) -> None:
    """
    Serve the Flask app.
    """
    app.run(debug=debug)
