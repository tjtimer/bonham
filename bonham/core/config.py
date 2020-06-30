"""
bonham

config

Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
created: 30.06.20
"""
import os
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_CONF = {
    'debug': True,
    'title': Path.cwd().stem,
    'host': 'localhost',
    'ports': [8080],
    'admin': os.getlogin(),
    'apps_path': Path.cwd() / 'apps',
    'apps_exclude': []
}


def load(path: Optional[str or Path] = None) -> dict:
    if path is None:
        path = Path.cwd() / 'conf' / 'app.conf.yaml'
    if Path(path).exists():
        with Path(path).open('r') as f:
            cfg = yaml.safe_load(f.read())
        DEFAULT_CONF.update(cfg)
    return {k.lower(): v for k, v in DEFAULT_CONF.items()}
