import logging
import json
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Преобразует лог в JSON и добавляет метаданные"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "metadata": {
                "file": record.filename,
                "line": record.lineno,
                "func": record.funcName,
                "logger_name": record.name
            }
        }

        if hasattr(record, "custom_extra"):
            log_data["metadata"].update(record.custom_extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class CustomAdapter(logging.LoggerAdapter):
    """Позволяет передавать любые аргументы как метаданные"""

    def process(self, msg, kwargs):
        extra = kwargs.pop("extra", {})
        extra.update(kwargs)
        return msg, {"extra": {"custom_extra": extra}}


def get_logger(name="AppLogger", level=logging.DEBUG):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return CustomAdapter(logger, {})