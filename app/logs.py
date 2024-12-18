import logging
import sys

from src.params.config import config

logging.basicConfig()


def get_logger(name: str, level: int = logging.INFO, tags: dict[str, str] | None = None, application: str = 'fastapi') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    # logger.addHandler(get_file_handler(f'logs/{name}.log', formatter, level))

    # logger.addHandler(get_loki_handler(
    #     tags=tags,
    #     application=application,
    # ))

    # logger.addHandler(get_stram_handler(formatter, level))

    return logger


def get_loki_handler(tags: dict[str, str] | None = None, application: str = 'fastapi'):
    loki_logs_handler_tags = {"application": application}
    if tags:
        loki_logs_handler_tags.update(tags)
    return LokiHandler(
        url=config.loki_url,
        tags=loki_logs_handler_tags,
        version="1"
    )

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
