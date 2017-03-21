import logging
import os

from bonham.settings import LOG_DIR, LOG_FILE, LOG_FORMAT, LOG_LEVEL, SERVER_NAME

__all__ = [
    "setup",
    ]


async def setup(app):
    print("start logger setup", flush=True)
    loggers = [
        logging.getLogger('aiohttp.access'),
        logging.getLogger('aiohttp.server')
        ]
    formatter = logging.Formatter(LOG_FORMAT)
    for logger in loggers:
        log_file = logging.FileHandler(os.path.join(LOG_DIR, f"{logger.name}.log"))
        log_file.setFormatter(formatter)
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(log_file)
    app.logger = logging.getLogger(f"{SERVER_NAME}.log")
    log_file = logging.FileHandler(LOG_FILE)
    log_file.setFormatter(formatter)
    app.logger.setLevel(LOG_LEVEL)
    app.logger.addHandler(log_file)
    print("end logger setup", flush=True)
