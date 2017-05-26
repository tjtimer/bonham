from setuptools import find_packages, setup

setup(
    name='bonham',
    version='0.0.1.dev1',
    description='aiohttp based web app',
    url='https://github.com/tjtimer/bonham',
    author='tjtimer',
    author_email='tjtimer@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points={
            'console_scripts': [
                    'bonham-run=bonham.root:run',
                    'bonham-create-app=bonham.bonham_development.create_app:run',
                    'bonham-dev-server=bonham.bonham_development.dev_server:run'
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
        'pytest', 'PyYaml', 'aiosmtpd', 'aiofiles', 'passlib', 'passlib'
        ]
    )
