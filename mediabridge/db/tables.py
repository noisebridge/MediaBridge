from functools import cache
from pathlib import Path

from sqlalchemy import Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DB_FILE = Path("/tmp/movies.sqlite")


class Base(DeclarativeBase):
    """Base class for all tables."""


class MovieTitle(Base):
    __tablename__ = "movie_title"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)


@cache
def get_engine() -> Engine:
    return create_engine(f"sqlite:///{DB_FILE}")


def create_tables() -> None:
    Base.metadata.create_all(get_engine())
