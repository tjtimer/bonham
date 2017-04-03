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
                        'bonham-run=bonham.root:main',
                        'bonham-create-app=bonham.bonham_development.create_app:main',
                        'bonham-dev-server=bonham.bonham_development.dev_server:main'
                        ],
                },
        zip_safe=False,
        install_requires=[
                'aiohttp',
                'aiofiles',
                'cchardet',
                'cryptography',
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
                'pytest',
                ]
        )
