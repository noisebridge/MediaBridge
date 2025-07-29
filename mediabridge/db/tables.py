from functools import cache

from sqlalchemy import REAL, ForeignKey, Integer, String, create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from mediabridge.definitions import DB_FILE, SQL_CONNECT_STRING


class Base(DeclarativeBase):
    """Base class for all tables."""


class MovieTitle(Base):
    __tablename__ = "movie_title"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)


_movie_fk = ForeignKey("movie_title.id")


class Rating(Base):
    __tablename__ = "rating"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[str] = mapped_column(String, _movie_fk, primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)


# (derived) reporting tables, denormalized for convenience so no JOIN is needed

_movie_fk = ForeignKey("movie_title.id")  # new key for a new table


class PopularMovie(Base):
    __tablename__ = "popular_movie"
    id: Mapped[str] = mapped_column(String, _movie_fk, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)  # denorm
    title: Mapped[str] = mapped_column(String, nullable=False)  # denorm


# We avoid using a SQL reserved keyword when naming columns, to avoid quoting.
POPULAR_MOVIE_QUERY = """
SELECT
    movie_id,
    COUNT(*) AS cnt,
    MAX(year) AS year,
    MAX(title) AS title
FROM rating
JOIN movie_title ON movie_id = id
GROUP BY movie_id
ORDER BY cnt DESC
"""

_user_fk = ForeignKey("rating.user_id")


class ProlificUser(Base):
    __tablename__ = "prolific_user"
    id: Mapped[int] = mapped_column(Integer, _user_fk, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    avg_rating: Mapped[float] = mapped_column(REAL, nullable=False)


PROLIFIC_USER_QUERY = """
SELECT
    CAST(user_id AS INTEGER),
    COUNT(*) AS cnt,
    ROUND(AVG(rating), 3) AS avg_rating
FROM rating
GROUP BY user_id
"""


@cache
def get_engine() -> Engine:
    DB_FILE.parent.mkdir(exist_ok=True)
    return create_engine(SQL_CONNECT_STRING)


def create_tables() -> None:
    Base.metadata.create_all(get_engine())


def table_exists(table_name: str) -> bool:
    inspector = inspect(get_engine())
    return inspector.has_table(table_name)
