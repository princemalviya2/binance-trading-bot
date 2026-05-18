"""
Logging configuration for the trading bot.
Sets up both a rotating file handler and a console handler.
"""

import logging
import logging.handlers
import os

LOG_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

LOG_FORMAT  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    if root.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Rotating file handler (10 MB, 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Console handler (WARNING+ so stdout stays clean)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)