"""A setuptools based setup module."""

from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gateway_addon',
    version='0.2.0',
    description='Bindings for Mozilla IoT Gateway add-ons',
    long_description=long_description,
    url='https://github.com/mozilla-iot/gateway-addon-python',
    author='Michael Stegeman',
    author_email='mrstegeman@gmail.com',
    keywords='mozilla iot gateway addon add-on',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['nnpy'],
)
