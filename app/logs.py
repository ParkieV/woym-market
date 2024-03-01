import logging
import sys

logging.basicConfig()


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    logger.addHandler(get_file_handler(f'logs/{name}.log', formatter))
    logger.addHandler(get_stram_handler(formatter, logging.DEBUG))

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
