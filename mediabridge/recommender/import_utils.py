# Utility functions (e.g., for building matrices)

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lightfm import LightFM


def import_lightfm_silently() -> "type[LightFM]":
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            "LightFM was compiled without OpenMP support",
            category=UserWarning,
        )
        from lightfm import LightFM

        assert isinstance(LightFM, type)

        return LightFM
