import sys
import logging.config

from src.params.config import config

LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'generic_console': {
            'format': '%(asctime)s [%(levelname)s] %(message)s (%(name)s:%(filename)s:%(funcName)s:%(lineno)d)',
        },
        'generic_json': {
            'class': 'logs_utils.JsonFormatter',
            'datefmt': '%Y-%m-%d %H:%M:%S.%f',
        }
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic_console',
            'stream': sys.stdout,
        },
        'console_error': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic_console',
            'stream': sys.stderr,
            'level': 'ERROR',
        },
        'file': {
            'class': 'logs_utils.CustomTimedRotatingFileHandler',
            'formatter': 'generic_json',
            'filename': 'app.log',
            'when': 'midnight',
            'interval': 1,
            'encoding': 'utf-8',
            'datefmt': '%Y-%m-%d',
        }
    },
    loggers={
        'woym_market': {
            'level': 'INFO' if config.mode == 'PROD' else 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'parser': {
            'level': 'INFO' if config.mode == 'PROD' else 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        # 'sqlalchemy': {
        #     'level': 'DEBUG',
        #     'handlers': ['file' if ],
        #     'propagate': False
        # }
    }
)

logging.config.dictConfig(LOGGING_CONFIG)

backend_logger = logging.getLogger('woym_market')
parser_logger = logging.getLogger('parser')

if config.loki_url:
    import logging_loki

    _loki_handler = logging_loki.LokiHandler(
        url=config.loki_url,
        tags={"app": "woym-market", "env": config.mode.lower()},
        version="1",
    )
    backend_logger.addHandler(_loki_handler)
    parser_logger.addHandler(_loki_handler)
