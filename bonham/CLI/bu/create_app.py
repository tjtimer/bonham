import os
from pathlib import Path

import arrow

from bonham.bonham_development.scaffold import scaffold
from bonham.settings import APPLICATION_NAME, SERVER_DIR


def ask_for_dir(config: dict, path: Path)-> dict:
    config['parent_dir'] = input(f"create app into {path} ? Type new path else Enter")
    if config['parent_dir'] is None:
        config['parent_dir'] = path
        config['app_dir'] = os.path.join(path, config['app_name'])
    else:
        config['app_dir'] = os.path.join(config['parent_dir'], config['app_name'])
    return config


def run(*, config=None):
    """
        config will be a dictionary with data we already got from the user, if he resumes from abortion
    """
    if config is None:
        print("create a new app. Type: CTRL+C to abort.")
        config = {
            'write': True,
            'backup_exists': False
            }
    c_keys = config.keys()
    try:
        if 'app_name' not in c_keys:
            name = input(
                    f"name of your app (will be prefixed with {APPLICATION_NAME}_,"
                    f" e.g. blog becomes {APPLICATION_NAME}_blog): ")
            config['app_name'] = f"{APPLICATION_NAME}_{name}"
        if 'app_dir' not in c_keys:
            config = ask_for_dir(config, SERVER_DIR)
        else:
            config = ask_for_dir(config, config['app_dir'])
        print(config['app_dir'])
        if os.path.exists(config['app_dir']):
            config['write'] = input(f"{config['app_dir']} already exists. Do you want to overwrite it? [y|n]")
            if config['write'] in 'nNnoNoNO':
                config['app_dir'] = input(f"absolute path: ")
            else:
                backup_name = f"BU_{config['app_dir']}_{arrow.now().datetime}"
                print(f"existing directory will be renamed to {backup_name}")
                os.rename(config['app_dir'],  backup_name)
                config['backup_exists'] = True

        if config['write']:
            os.mkdir(config['app_dir'])
            print(f"scaffolding your app now.")
            scaffold(config)
        else:
            cancel = input("Start again or cancel? [ Enter | c ]")
            if not cancel:
                run()
    except KeyboardInterrupt:
        not_cancel = input("\nCancel? [ Enter | N ]")
        if not_cancel:
            run(config=config)
