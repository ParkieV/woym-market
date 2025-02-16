import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from venv import logger

import dateutil.parser


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "timestamp": self.formatTime(record),
            "message": record.getMessage(),
            "name": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        return json.dumps(log_record, ensure_ascii=False)

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when, interval, backupCount=0, encoding='utf-8', logger_name="default", datefmt=None):
        self.datefmt = datefmt
        super().__init__('/dev/null', when, interval, backupCount, encoding=encoding, utc=True)

    def _generate_timestamp(self, str_timestamp: str):
        return dateutil.parser.parse(str_timestamp).strftime(self.datefmt)


    def emit(self, record):
        """Перед каждым логированием обновляем путь к файлу с учетом имени логера."""
        if self.baseFilename == "/dev/null":
            self.stream = open(
                self.get_filename_stream(
                    record.name,
                    self._generate_timestamp(record.asctime if 'asctime' in record.__dict__ else datetime.now().isoformat()),
                ),
                "a",
                encoding=self.encoding
            )
        super().emit(record)

    def get_filename_stream(self, logger_name, timestamp: str = None):
        # Составляем путь с учетом имени логгера
        filepath = f"logs/{logger_name}"
        os.makedirs(filepath, exist_ok=True)
        return f"{filepath}/{logger_name}_{timestamp or ''}.log"
