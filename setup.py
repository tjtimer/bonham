from setuptools import setup

setup(
        name='bonham',
        version='0.0.1',
        description='aiohttp based web server',
        url='https://github.com/tjtimer/bonham',
        author='tjtimer',
        author_email='tjtimer@gmail.com',
        license='MIT',
        packages=['bonham', 'bonham/bonham_development'],
        entry_points={
            'console_scripts': ['bonham-create-app=bonham.bonham_development.create_app:main'],
        },
        zip_safe=False,
        install_requires=[
            'aiohttp',
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
            'pytest'
        ]
)
