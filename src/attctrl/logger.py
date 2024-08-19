import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import ClassVar, Dict, List, Optional


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS: ClassVar[Dict[int, str]] = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomFilter(logging.Filter):
    def __init__(self, allow_repeats) -> None:
        super().__init__()
        self.allow_repeats = allow_repeats
        self.last_msg: Optional[str] = None

    def filter(self, record: logging.LogRecord) -> bool:
        if self.allow_repeats:
            return True
        msg = record.getMessage()

        if self.last_msg is None:
            self.last_msg = msg
            return True

        are_different = msg != self.last_msg
        self.last_msg = msg
        return are_different


def new_logger(
    name: str, level: str = "DEBUG", no_repeat: bool = False, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Create a logger with a custom formatter.

    :param name: Name of the logger
    :param log_file: Path to the log file (optional)
    :param level: Logging level
    :return: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Create console handler with custom formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # No repeat filter
    logger.addFilter(CustomFilter(not no_repeat))

    # If log file is provided, create file handler
    if log_file:
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


class LoggerGlobalFileHandler:
    def __init__(self, logfile: Path) -> None:
        self.loggers: List[logging.Logger] = [
            logger
            for logger in logging.root.manager.loggerDict.values()
            if isinstance(logger, logging.Logger)
        ]
        logfile.parent.mkdir(exist_ok=True)
        self.loghandler = logging.FileHandler(logfile)
        self.loghandler.setFormatter(CustomFormatter())

    def start(self):
        for logger in self.loggers:
            logger.addHandler(self.loghandler)

    def finish(self):
        for logger in self.loggers:
            logger.removeHandler(self.loghandler)

    def teardown(self):
        self.finish()
        del self.loghandler

    def __del__(self):
        self.teardown()
