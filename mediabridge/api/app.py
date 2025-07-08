import os

import typer
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from mediabridge.config.backend import ENV_TO_CONFIG
from mediabridge.db.tables import Base
from mediabridge.recommender.make_recommendation import get_title, recommend

typer_app = typer.Typer()
db = SQLAlchemy(model_class=Base)


# Please consider the arguments in
# https://flask.palletsprojects.com/en/stable/patterns/appfactories
# when making edits to the create_app() function.
def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    config = ENV_TO_CONFIG.get(config_name)
    if config is None:
        raise ValueError(f"Could not find Flask API config for name: {config_name}")

    app = Flask(__name__)
    app.config.from_object(config)

    CORS(app)
    # Configure Flask-SQLAlchemy
    db.init_app(app)

    @app.route("/")  # type: ignore
    def hello_world() -> str:
        return "MediaBridge API is running!"

    @app.route("/api/v1/movie/search")  # type: ignore
    def search_movies() -> tuple[Response, int]:
        query = request.args.get("q")
        if not query:
            return jsonify({"error": "Query parameter 'q' is required."}), 400

        with db.engine.connect() as conn:
            pattern = f"%{query}%"
            movies = conn.execute(
                text(
                    "SELECT * FROM movie_title WHERE LOWER(title) LIKE LOWER(:pattern) LIMIT 10"
                ),
                {"pattern": pattern},
            ).fetchall()
            movies_list = [row._asdict() for row in movies]
            return jsonify(movies_list), 200

    @app.route("/api/v1/movie/recommend", methods=["GET"])  # type: ignore
    def recommend_movies() -> tuple[Response, int]:
        data = request.get_json()
        if not data or "movies" not in data:
            return jsonify({"error": "JSON body with 'movies' array is required."}), 400
        movies = data["movies"]
        if not isinstance(movies, list) or not all(isinstance(m, int) for m in movies):
            return jsonify({"error": "'movies' must be a list of integers."}), 400

        try:
            rec_ids = recommend()
            rec_titles = [get_title(int(mid)) for mid in rec_ids]
        except Exception as e:
            return jsonify({"error": f"Recommendation failed: {str(e)}"}), 500

        return jsonify({"recommendations": rec_titles}), 200

    return app


@typer_app.command()
def serve(ctx: typer.Context, debug: bool = True) -> None:
    """
    Serve the Flask app.
    """
    app = create_app()
    app.run(debug=debug)
