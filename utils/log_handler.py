"""Integration with Loguru"""

import logging
from logging import Handler, LogRecord
from loguru import logger


class LogHandler(Handler):
    def emit(self, record: LogRecord):
        level: str = str(record.levelno)
        frame = logging.currentframe()
        depth: int = 2

        try:
            level = logger.level(record.levelname).name
        except ValueError as e:
            logger.opt(exception=e).trace(
                "Failed to determine logger intercept level")

        while frame and frame.f_code.co_filename == logging.__file__:
            if frame.f_back is not None:
                frame = frame.f_back
            else:
                break
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
