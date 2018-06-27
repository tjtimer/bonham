# bonham create_config
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
import re


def get_version():
    v = input('Application version: ')
    valid = re.match(r"(\d+\.){2}\d+([alphALPHbetBETdvomnDVOMN]*\d*)?", v)
    if valid:
        return v
    raise ValueError(f"{v} is not a valid version declaration. (e.g. 0.0.1.dev, 0.1.2a2 etc.)")


def get_title():
    v = input('Application title: ')
    return v


def collect_data(conf: dict = None):
    if conf is None:
        conf = {}
    try:
        if 'title' not in conf.keys():
            conf['title'] = get_title()
        if 'version' not in conf.keys():
            conf['version'] = get_version()
    except ValueError as v:
        print(v.args[0])
        return collect_data(conf)
