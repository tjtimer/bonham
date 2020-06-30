from setuptools import find_packages, setup

from __version__ import VERSION

with open('README.md', 'r') as readme:
    long_desc = readme.read()

setup(
    name='bonham',
    version=VERSION,
    description='Python web app.',
    long_description=long_desc,
    url='https://github.com/tjtimer/bonham',
    author='Tim "tjtimer" Jedro',
    author_email='tjtimer@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bonham=bonham.app:run'
        ]
    },
    zip_safe=False,
    install_requires=[
        'aiohttp',
        'aiohttp-graphql',
        'aiojobs',
        'cryptography',
        'graphene',
        'htmldoom',
        'hypothesis',
        'inflect',
        'javascripthon',
        'passlib',
        'pytest',
        'pytest-aiohttp',
        'PyYaml'
    ],
    extra_requires=(
        'cchardet',
        'uvloop',
        'ujson'
    )
)
