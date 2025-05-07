from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from mediabridge.api.app import create_app, db


def app() -> Generator[Flask, None, None]:
    """Instantiate the Flask app for testing and yield it.

    This fixture creates a new Flask app instance for each test, sets up the
    database, and tears it down after the test is complete.
    """
    app = create_app("testing")

    with app.app_context():
        # Create the database tables (this is an empty in-memory database)
        db.create_all()

        # By yielding the app, we provide the current value to tests which
        # use this fixture. After the test is done, the rest of the code in this
        # function is executed.
        yield app

        # Drop everything, so the next test starts with a clean slate
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    """Create a test client for the Flask app and yield it.

    By using yield, we ensure that the test using this fixture is running
    inside of the test_client contenxt, which allows us to make requests to the
    app and get responses back.

    Note that this fixture itself depends on the app fixture.
    """
    with app.test_client() as client:
        yield client
