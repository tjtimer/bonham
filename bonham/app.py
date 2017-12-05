"""
:Package: bonham
:Module: app
:Author: Tim "tjtimer" Jedro
:Email: tjtimer@gmail.com

:Version: 0.0.1.dev
:Created: 05.12.17
"""
import os

__all__ = ('run',)

DEFAULT_CONF_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'server.conf.yaml'
    )


def run(*,
        conf: dict = None,
        conf_path: str = DEFAULT_CONF_PATH):
    """
    runs application

    Args:
        conf (dict): see :ref:configuration.rst
        
        conf_path (str): a path to a yaml configuration file
        defaults to a file named 'server.conf.yaml'
        in your current working directory
    """
    print(conf)
    print(conf_path)


if __name__ == '__main__':
    run()
