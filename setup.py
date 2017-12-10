from setuptools import find_packages, setup

setup(
    name='bonham',
    version='0.0.1.dev',
    description='aiohttp based web app',
    url='https://github.com/tjtimer/bonham',
    author='Tim "tjtimer" Jedro',
    author_email='tjtimer@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_dir={'bonham': 'bonham'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bonham-run=bonham.app:run',
            ]
        },
    zip_safe=False,
    install_requires=[
        'aiohttp', 'aiodocker', 'uvloop',
        'PyYaml', 'aiohttp_jinja2'
        ]
    )
