import sys

from loguru import logger


def setup_logging(debug: bool):
    """
    Configure logging based on debug mode.

    Args:
        debug (bool): If True, shows all log levels including DEBUG.
                     If False, shows INFO and above with a cleaner format.
    """
    logger.remove()  # Remove default handler

    if debug:
        # Debug mode: Show timestamp, level, and full context
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )
    else:
        # Normal mode: Clean format for INFO and above, no DEBUG messages
        logger.add(
            sys.stderr,
            level="INFO",
            format="{message}",  # Simply show the message
            filter=lambda record: record["level"].name != "DEBUG",
        )

        # Optional: Add separate handler for warnings and errors with more context
        logger.add(
            sys.stderr,
            level="WARNING",
            format="<yellow>{level}: {message}</yellow>",
            filter=lambda record: record["level"].name in ("WARNING", "ERROR", "CRITICAL"),
        )
