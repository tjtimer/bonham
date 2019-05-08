"""
cli.py
author: Tim "tjtimer" Jedro
created: 08.05.19
"""
import click
from pathlib import Path

import yaml

from bonham import project

HOME = Path.home()
BONHAM_DIR = HOME / '.local' / 'bonham'
BONHAM_CONFIG = BONHAM_DIR / 'config.yml'

cfg = {
    'root': None,
    'projects': {}
}

if not BONHAM_DIR.is_dir():
    BONHAM_DIR.mkdir()
    BONHAM_CONFIG.touch()

with BONHAM_CONFIG.open('r+') as f:
    try:
        cfg.update(yaml.safe_load(f.read()))
    except TypeError:
        pass
    if cfg['root'] is None:
        root = Path.cwd()
        cfg['root'] = str(root)
        f.write(yaml.safe_dump(cfg))
    else:
        root = Path(cfg['root'])


@click.group()
def cli():
    """Welcome to Bonham! Manage your web projects from start to end."""


@cli.command('start')
@click.option('--name', prompt='project name: ')
def new_project(name):
    project.create(root, name)
