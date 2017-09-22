import datetime
import os

from setuptools import find_packages, setup

setup(
        name='bonham',
    version=f"0.0.1.dev1-{datetime.datetime.now()}",
        description='aiohttp based web app',
        url='https://github.com/tjtimer/bonham',
        author='Tim "tjtimer" Jedro',
        author_email='tjtimer@gmail.com',
        license='MIT',
        packages=find_packages(where=os.path.dirname(__file__)),
        entry_points={
            'console_scripts': [
                'bonham-run=bonham.root:run',
                'bonham-dev-server=bonham.bonham_CLI.dev_server:run'
                ],
            },
        zip_safe=False,
        install_requires=[
            'aiohttp',
            'cchardet',
            'cryptography',
            'curio',
            'uvloop',
            'sqlalchemy',
            'asyncpg',
            'jinja2',
            'aiohttp_jinja2',
            'sqlamp',
            'PyJWT',
            'arrow',
            'requests',
            'hypothesis',
            'pytest', 'PyYaml', 'aiosmtpd', 'aiofiles', 'passlib'
            ]
        )
