from flask.testing import FlaskClient
from sqlalchemy import text

from mediabridge.api.app import create_app, db


class MovieSearchTest:
    def _insert_movies(self) -> None:
        ins = """
                INSERT INTO movie_title (id, year, title)
                VALUES ('1', 2010, 'Inception'),
                       ('2', 1999, 'The Matrix'),
                       ('3', 1994, 'The Shawshank Redemption'),
                       ('4', 1994, 'Toy Story')
                """
        with db.engine.connect() as conn:
            conn.execute(text(ins))
            conn.commit()

    def test_create_app_cleanly(self) -> None:
        create_app("testing")

    def test_movie_search(self, client: FlaskClient) -> None:
        self._insert_movies()
        response = client.get("/api/v1/movie/search?q=Inception")
        assert response.status_code == 200
        data = response.get_json()
        assert data == [{"id": "1", "year": 2010, "title": "Inception"}]

    def test_movie_search_multiple_results(self, client: FlaskClient) -> None:
        self._insert_movies()
        response = client.get("/api/v1/movie/search?q=tion")
        assert response.status_code == 200
        data = response.get_json()
        assert data == [
            {"id": "1", "year": 2010, "title": "Inception"},
            {"id": "3", "year": 1994, "title": "The Shawshank Redemption"},
        ]

    def test_movie_search_no_results(self, client: FlaskClient) -> None:
        self._insert_movies()
        response = client.get("/api/v1/movie/search?q=NonExistentMovie")
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_movie_search_missing_query(self, client: FlaskClient) -> None:
        response = client.get("/api/v1/movie/search")
        assert response.status_code == 400
        data = response.get_json()
        assert data == {"error": "Query parameter 'q' is required."}
