from sqlalchemy import text

from mediabridge.api.app import create_app, db


class MovieSearchTest:
    def _insert_movies(self):
        with db.engine.connect() as conn:
            conn.execute(
                text("""
                INSERT INTO movie_title (id, year, title)
                VALUES ('1', 2010, 'Inception'),
                       ('2', 1999, 'The Matrix'),
                       ('3', 1994, 'The Shawshank Redemption'),
                       ('4', 1994, 'Toy Story')
                """)
            )
            conn.commit()

    def test_create_app_cleanly(self):
        create_app("testing")

    def test_movie_search(self, client):
        self._insert_movies()
        # Test the search_movies endpoint
        response = client.get("/api/v1/movie/search?q=Inception")
        assert response.status_code == 200
        data = response.get_json()
        assert data == [{"id": "1", "year": 2010, "title": "Inception"}]

    def test_movie_search_multiple_results(self, client):
        self._insert_movies()
        # Test the search_movies endpoint
        response = client.get("/api/v1/movie/search?q=tion")
        assert response.status_code == 200
        data = response.get_json()
        assert data == [
            {"id": "1", "year": 2010, "title": "Inception"},
            {"id": "3", "year": 1994, "title": "The Shawshank Redemption"},
        ]

    def test_movie_search_no_results(self, client):
        self._insert_movies()
        # Test the search_movies endpoint with no results
        response = client.get("/api/v1/movie/search?q=NonExistentMovie")
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_movie_search_missing_query(self, client):
        response = client.get("/api/v1/movie/search")
        assert response.status_code == 400
        data = response.get_json()
        assert data == {"error": "Query parameter 'q' is required."}
