"""
Recommends movies based on sparse input: the "cold start" problem.
"""

from lightfm import LightFM


def recommend() -> None:
    model = LightFM(no_components=30)
    print("\n", model)
