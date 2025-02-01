from functools import cache
from pathlib import Path

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

DB_FILE: Path = Path("/tmp/movies.sqlite")

Base = declarative_base()


class MovieTitle(Base):
    __tablename__ = "movie_title"
    id: Column = Column(String, primary_key=True)
    year: Column = Column(Integer)
    title: Column = Column(String, nullable=False)


@cache
def get_engine() -> Engine:
    return create_engine(f"sqlite:///{DB_FILE}")


def create_tables() -> None:
    Base.metadata.create_all(get_engine())
