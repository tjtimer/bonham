from setuptools import find_packages, setup

setup(
    name='bonham',
    version=f"0.0.1.dev",
    description='aiohttp based web app',
    url='https://github.com/tjtimer/bonham',
    author='Tim "tjtimer" Jedro',
    author_email='tjtimer@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_dir={'': 'bonham'},
    entry_points={'console_scripts': []},
    zip_safe=False,
    install_requires=[]
    )
