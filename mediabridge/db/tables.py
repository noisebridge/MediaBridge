from functools import cache

from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from mediabridge.definitions import OUTPUT_DIR

DB_FILE = OUTPUT_DIR / "movies.sqlite"


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
    movie_id: Mapped[str] = mapped_column(String, _movie_fk, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)


# (derived) reporting tables, denormalized for convenience so no JOIN is needed


class PopularMovie(Base):
    __tablename__ = "popular_movie"
    id: Mapped[str] = mapped_column(String, _movie_fk, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)  # denorm
    title: Mapped[str] = mapped_column(String, nullable=False)  # denorm


_user_fk = ForeignKey("rating.user_id")


class ProlificUser(Base):
    __tablename__ = "prolific_user"
    id: Mapped[int] = mapped_column(Integer, _user_fk, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    avg_rating: Mapped[float] = mapped_column(Integer, nullable=False)


@cache
def get_engine() -> Engine:
    DB_FILE.parent.mkdir(exist_ok=True)
    return create_engine(f"sqlite:///{DB_FILE}")


def create_tables() -> None:
    Base.metadata.create_all(get_engine())
