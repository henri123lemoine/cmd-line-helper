import sys

from loguru import logger


def setup_logging(debug: bool):
    """Configure logging based on debug mode."""
    logger.remove()
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="ERROR")
