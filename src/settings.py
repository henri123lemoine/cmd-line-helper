import logging.config
import os
from datetime import datetime
from pathlib import Path

import anthropic
import openai
from dotenv import load_dotenv

load_dotenv()

# General
DATE = datetime.now().strftime("%Y-%m-%d")
PROJECT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_PATH / "data"
os.makedirs(DATA_PATH, exist_ok=True)

# Clients

## OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_CLIENT = openai.Client(api_key=OPENAI_API_KEY)

# Logging

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {"": {"handlers": ["default"], "level": "INFO", "propagate": True}},
}

logging.config.dictConfig(LOGGING_CONFIG)
