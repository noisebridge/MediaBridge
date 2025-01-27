from collections.abc import Iterator
from contextlib import _GeneratorContextManager, contextmanager
from logging import Handler, Logger, LogRecord


def silence_logging(logger: Logger) -> _GeneratorContextManager[None]:
    """A helper context manager to suppress logs from cluttering test output."""

    class NullHandler(Handler):
        def emit(self, record: LogRecord) -> None:
            pass  # Ignore all log records

    @contextmanager
    def _silence_logging() -> Iterator[None]:
        original_handlers = logger.handlers.copy()
        logger.handlers.clear()
        logger.addHandler(NullHandler())

        try:
            yield  # Let the test code run for a bit.
        finally:
            logger.handlers = original_handlers  # Turn logging back on.

    return _silence_logging()
