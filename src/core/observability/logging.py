"""
Logging utilities with colored output for better readability.
"""

import sys
import logging


class ColorLogger:
    """
    A class-based logger with colored output for better readability.

    Features:
    - Colors log messages based on level
    - Provides convenience method for structured logging
    """

    COLORS = {
        "DEBUG": "\033[37m",     # White
        "INFO": "\033[36m",      # Cyan
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m",      # Reset
    }

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize the ColorLogger instance.

        :param name: Logger name (usually __name__)
        :param level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.hasHandlers():
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)
            handler.setFormatter(self.ColorFormatter())
            self.logger.addHandler(handler)

    class ColorFormatter(logging.Formatter):
        """
        Custom logging formatter that applies colors to level name and message.
        """
        def format(self, record: logging.LogRecord) -> str:
            color = ColorLogger.COLORS.get(record.levelname, ColorLogger.COLORS["RESET"])
            record.levelname = f"{color}{record.levelname}{ColorLogger.COLORS['RESET']}"
            record.msg = f"{color}{record.msg}{ColorLogger.COLORS['RESET']}"
            return super().format(record)

    def log(self, title: str, info: str, level: int = logging.INFO) -> None:
        """
        Log a structured message with title and info.

        :param title: Short header for the log
        :param info: Detailed information to log
        :param level: Logging level
        """
        log_func = {
            logging.DEBUG: self.logger.debug,
            logging.INFO: self.logger.info,
            logging.WARNING: self.logger.warning,
            logging.ERROR: self.logger.error,
            logging.CRITICAL: self.logger.critical,
        }.get(level, self.logger.info)

        separator = "=" * 80
        log_func(separator)
        log_func(title)
        log_func(info)
        log_func(separator)


logger = ColorLogger(__name__).logger
