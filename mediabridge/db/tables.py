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


class RatingTemp(Base):
    __tablename__ = "rating_temp"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)


@cache
def get_engine() -> Engine:
    return create_engine(f"sqlite:///{DB_FILE}")


def create_tables() -> None:
    Base.metadata.create_all(get_engine())
