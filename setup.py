from setuptools import find_packages, setup

setup(
    name='bonham',
    version='0.0.1.dev',
    description='CLI tool for web app projects with python and Vue.js.',
    url='https://github.com/tjtimer/bonham',
    author='Tim "tjtimer" Jedro',
    author_email='tjtimer@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bonham=bonham.cli:cli'
        ]
    },
    zip_safe=False,
    install_requires=[
        'click',
        'sanic',
        'aiofiles',
        'passlib',
        'PyYaml',
        'PyJWT',
        'cryptography',
        'pytest',
        'pytest-sanic',
        'pytest-aiohttp',
        'jinja2-sanic',
        'hypothesis'
    ]
)
