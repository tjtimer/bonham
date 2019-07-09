from setuptools import find_packages, setup

setup(
    name='bonham',
    version='0.0.1.dev',
    description='Progressive web app development made easy.',
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
        'curio',
        'inflect',
        'pytest',
        'pytest-aiohttp',
        'hypothesis'
    ]
)
