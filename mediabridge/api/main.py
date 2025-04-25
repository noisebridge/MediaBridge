import flask
import typer

typer_app = typer.Typer()


def create_app():
    app = flask.Flask(__name__)

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    return app


@typer_app.command()
def serve(ctx: typer.Context, debug: bool = True):
    """
    Serve the Flask app.
    """
    app = create_app()
    app.run(debug=debug)
