from setuptools import setup

setup(name='bonham',
      version='0.0.1',
      description='aiohttp based web server',
      url='https://github.com/tjtimer/bonham',
      author='tjtimer',
      author_email='tjtimer@gmail.com',
      license='MIT',
      packages=['bonham'],
      zip_safe=False,
      install_requires=['aiohttp',
                        'uvloop',
                        'sqlalchemy',
                        'asyncpg'])
