from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='async_robin_stocks',
      version='3.3.38',
      description='An asynchronous fork of the popular Python wrapper around the Robinhood API originally written by Josh Fernandes',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='https://github.com/rekeshali/async_robin_stocks',
      author='Rekesh Ali',
      author_email='rekeshali@gmail.com',
      keywords=['robinhood','robin stocks','finance app','stocks','options','trading','investing','asynchronous','async'],
      license='MIT',
      python_requires='>=3.9',
      packages=find_packages(),
      requires=['requests', 'pyotp', 'cryptography'],
      install_requires=[
          'requests',
          'pyotp',
          'python-dotenv',
          'cryptography',
          'aiofiles',
          'aiohttp',
          'aiologger'
      ],
      zip_safe=False)
