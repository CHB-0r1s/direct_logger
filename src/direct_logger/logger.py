import logging
import json
import sys
import os
from datetime import datetime


class JsonFormatter(logging.Formatter):
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
    def process(self, msg, kwargs):
        extra = kwargs.pop("extra", {})
        extra.update(kwargs)
        return msg, {"extra": {"custom_extra": extra}}


def get_logger(name="AppLogger", level=logging.DEBUG, log_file=None, to_console=True):
    """
    :param name: Имя логгера
    :param level: Уровень логирования
    :param log_file: Путь к файлу (если нужно писать в файл)
    :param to_console: Если False, вывод в терминал будет отключен
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)
    formatter = JsonFormatter()

    if to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return CustomAdapter(logger, {})