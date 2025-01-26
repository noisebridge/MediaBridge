from contextlib import contextmanager
from logging import Handler, Logger


def silence_logging(self, logger: Logger):
    """A helper context manager to suppress logs from cluttering test output."""

    class NullHandler(Handler):
        def emit(self, record):
            pass  # Ignore all log records

    @contextmanager
    def _silence_logging():
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()
        logger.addHandler(NullHandler())

        try:
            yield  # Let the test code run for a bit.
        finally:
            logger.handlers = original_handlers  # Turn logging back on.

    return _silence_logging()
