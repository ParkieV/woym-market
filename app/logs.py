import logging
import sys
from logging_loki import LokiQueueHandler, LokiHandler

logging.basicConfig()


def get_logger(name: str, level: int = logging.INFO, tags: dict[str, str] | None = None, application: str = 'fastapi') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    logger.addHandler(get_file_handler(f'logs/{name}.log', formatter, level))

    loki_logs_handler_tags = {"application": application}
    if tags:
        loki_logs_handler_tags.update(tags)
    loki_logs_handler = LokiHandler(
        url="http://localhost:3100/loki/api/v1/push",
        tags=loki_logs_handler_tags,
        version="1"
    )
    logger.addHandler(loki_logs_handler)

    # logger.addHandler(get_stram_handler(formatter, level))

    return logger


def get_file_handler(filename: str, formatter: logging.Formatter, level: int = logging.WARNING) -> logging.Handler:
    handler = logging.FileHandler(filename, mode='a')
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def get_stram_handler(formatter: logging.Formatter, level: int = logging.INFO) -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler
