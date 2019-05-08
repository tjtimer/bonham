"""
project.py
author: Tim "tjtimer" Jedro
created: 08.05.19
"""
import os
import venv
from pathlib import Path

PUBLIC_DIRS = ['static', 'media']
SERV_DIRS = ['conf.d', 'app', 'tmp', 'log']


def create(root: Path, name: str):
    print(f'Creating new project {name} at {root}.')
    prj_dir = root / name
    prj_dir.mkdir()
    dev_dir = prj_dir / 'dev'
    dev_dir.mkdir()
    pub_dir = dev_dir / 'public'
    pub_dir.mkdir()
    for d in PUBLIC_DIRS:
        (pub_dir / d).mkdir()
    serv_dir = dev_dir / 'serv'
    serv_dir.mkdir()
    for d in SERV_DIRS:
        (serv_dir / d).mkdir()
    env_dir = serv_dir / '.venv'
    v = venv.EnvBuilder(with_pip=True, prompt=True)
    context = v.ensure_directories(str(env_dir))
    v.create_configuration(context)
    v.setup_python(context)
    v.setup_scripts(context)
    v.post_setup(context)
    print('It\'s done!')

