import flask
import typer
from flask_cors import CORS
from sqlalchemy import text

from mediabridge.db.tables import get_engine

typer_app = typer.Typer()


def create_app():
    app = flask.Flask(__name__)
    CORS(app)

    @app.route("/")
    def hello_world():
        return "MediaBridge API is running!"

    @app.route("/api/v1/movie/search")
    def search_movies():
        query = flask.request.args.get("q")
        if not query:
            return flask.jsonify({"error": "Query parameter 'q' is required."}), 400

        with get_engine().connect() as conn:
            pattern = f"%{query}%"
            movies = conn.execute(
                text("SELECT * FROM movie_title WHERE title LIKE :pattern LIMIT 10"),
                {"pattern": pattern},
            ).fetchall()
            movies_list = [row._asdict() for row in movies]
            return flask.jsonify(movies_list)

    return app


@typer_app.command()
def serve(ctx: typer.Context, debug: bool = True):
    """
    Serve the Flask app.
    """
    app = create_app()
    app.run(debug=debug)
