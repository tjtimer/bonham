"""
Bonham Root
Author: Tim "tjtimer" Jedro
version: 0.0.1dev
"""
import asyncio
import logging.config
from pathlib import Path

import uvloop

from bonham.bonham_core.helper import load_yaml_conf
from bonham.bonham_core.service import Service
from bonham.settings import CONF_DIR

__all__ = (
    'run',
    )
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger_config = load_yaml_conf(Path(CONF_DIR).joinpath('logging.conf.yaml'))
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)


def run():
    """Simple `run` example.
    Instantiate a service.
    Install your components.
    Run your service.
    """
    service = Service('/var/www/tjtimer.com/server/conf/server.conf.yaml')
    service.run()


if __name__ == '__main__':
    run()
