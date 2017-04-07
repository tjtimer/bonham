#!/usr/bin/env python
import os

from bonham.settings import SERVER_NAME, SERVER_ROOT


def main(*, config=None):
    print("create a new app. Type: CTRL+C to abort.")
    """
        config will be a dictionary with data we already got from the user, if he resumes from abortion
    """
    if config is None:
        config = {
            'write': True
        }
    print(config)
    c_keys = config.keys()
    try:
        if 'app_name' not in c_keys:
            config['app_name'] = input(
                f"name of your app (will be prefixed with {SERVER_NAME}_, e.g. {SERVER_NAME}_blog): ")
        if 'app_dir' not in c_keys:
            config['parent_dir'] = input(f"create app into {SERVER_ROOT} ? Type new path else Enter")
            if config['parent_dir'] is None:
                config['app_dir'] = os.path.join(SERVER_ROOT, config['app_name'])
            else:
                config['app_dir'] = os.path.join(config['parent_dir'], config['app_name'])

        print(config['app_dir'])
        if os.path.exists(config['app_dir']):
            config['write'] = input(f"{config['app_dir']} already exists. Do you want to overwrite it? [y|n]")
            if config['write'] in 'nNnoNoNO':
                config['app_dir'] = input(f"type absolute app path: ")

        if config['write']:
            os.mkdir(config['app_dir'])
            init_file = os.path.join(config['app_dir'], '__init__.py')
            ifl = open(init_file, 'wb')
            ifl.close()
        else:
            cancel = input("Start again or cancel? [ Enter | c ]")
            if not cancel:
                main()
    except KeyboardInterrupt:
        not_cancel = input("\nCancel? [ Enter | N ]")
        if not_cancel:
            main(config=config)
