from dataclasses import dataclass


@dataclass(order=True)
class MovieData:
    """Dataclass for known data from the Netflix dataset"""

    netflix_id: str
    title: str
    year: int

    def flatten_values(self) -> dict[str, str]:
        """Format all dataclass fields into a mapping of strings by joining
        lists with semicolons"""
        return {
            k: (";".join(v) if isinstance(v, list) else str(v))
            for (k, v) in vars(self).items()
        }


@dataclass(order=True)
class EnrichedMovieData(MovieData):
    """Dataclass for enriched data from a Wikidata match"""

    wikidata_id: str
    genres: list[str]  # possibly an empty list
    director: str | None
