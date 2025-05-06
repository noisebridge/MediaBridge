import typer
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from sqlalchemy import text

from mediabridge.db.tables import get_engine

typer_app = typer.Typer()

# Please consider the arguments in
# https://flask.palletsprojects.com/en/stable/patterns/appfactories
# when making edits to the create_app() function.
def create_app() -> Flask:
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
            pattern = f"%{query}%"
            movies = conn.execute(
                text(
                    "SELECT * FROM movie_title WHERE LOWER(title) LIKE LOWER(:pattern) LIMIT 10"
                ),
                {"pattern": pattern},
            ).fetchall()
            movies_list = [row._asdict() for row in movies]
            return jsonify(movies_list), 200

    return app


@typer_app.command()
def serve(ctx: typer.Context, debug: bool = True) -> None:
    """
    Serve the Flask app.
    """
    app.run(debug=debug)
