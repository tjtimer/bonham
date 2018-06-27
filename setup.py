from setuptools import find_packages, setup

setup(
    name='bonham',
    version='0.0.1.dev',
    description='python aiohttp based web app',
    url='https://github.com/tjtimer/bonham',
    author='Tim "tjtimer" Jedro',
    author_email='tjtimer@gmail.com', license='MIT', packages=find_packages('bonham'),
    package_dir={'bonham': 'bonham'},
    include_package_data=True,
    entry_points={
        'console_scripts': [  # 'bonham-run=bonham.app:run',
            # 'bonham-init=bonham.CLI.init_project:run', 'bonham-create=bonham.CLI.create:run',
            ]
        },
    zip_safe=False, install_requires=['aiohttp', 'aiohttp_jinja2', 'passlib', 'PyYaml', 'PyJWT'
                                      ]
    )
