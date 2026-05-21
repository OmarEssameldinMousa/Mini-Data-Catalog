from pythonjsonlogger.jsonlogger import JsonFormatter
import logging
import logging.config

from app.middleware.correlation import get_correlation_id


class CorrelationIDFilter(logging.Filter):
    """
    Inject correlation_id into every log record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


class ServiceNameFilter(logging.Filter):
    """
    Inject static service_name into every log record.
    """

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.service_name = self.service_name
        return True


def setup_logging(service_name: str, debug: bool = False) -> None:

    log_level = "DEBUG" if debug else "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,

        "filters": {
            "correlation_id": {
                "()": CorrelationIDFilter,
            },

            "service_name": {
                "()": ServiceNameFilter,
                "service_name": service_name,
            },
        },

        "formatters": {
            "json": {
                "()": JsonFormatter,

                "format": (
                    "%(asctime)s "
                    "%(name)s "
                    "%(levelname)s "
                    "%(message)s "
                    "%(correlation_id)s "
                    "%(service_name)s"
                ),
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": [
                    "correlation_id",
                    "service_name",
                ],
                "level": log_level,
            }
        },

        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
    }

    logging.config.dictConfig(logging_config)