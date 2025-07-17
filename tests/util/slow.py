from os import getenv
from typing import Any, Callable


def mark_slow_integration_test(test_func: Callable[..., None]) -> Callable[..., None]:
    """
    Marks a "slow" test that we may wish to skip.

    The decorated TestCase function won't be run
    when we set environment variable SKIP_SLOW=1.
    """
    should_skip = getenv("SKIP_SLOW", "0") == "1"
    if should_skip:
        return do_nothing
    else:
        return test_func


def do_nothing(self: Any) -> None:
    self.assertTrue(self)
