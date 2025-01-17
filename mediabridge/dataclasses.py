from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MovieData:
    netflix_id: int
    title: str
    year: int


@dataclass
class EnrichedMovieData(MovieData):
    wikidata_id: str
    genres: Optional[List[str]]
    director: Optional[str]
