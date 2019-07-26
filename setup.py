"""A setuptools based setup module."""

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requirements = [
    'nnpy==1.4.2',
]

if sys.version_info.major == 2:
    requirements.append('jsonschema==2.6.*')
elif sys.version_info.major == 3:
    if sys.version_info.minor < 5:
        requirements.append('jsonschema==2.6.*')
    else:
        requirements.append('jsonschema>=3.0.0')

from gateway_addon import __version__

setup(
    name='gateway_addon',
    version=__version__,
    description='Bindings for Mozilla WebThings Gateway add-ons',
    long_description=long_description,
    url='https://github.com/mozilla-iot/gateway-addon-python',
    author='Mozilla IoT',
    keywords='mozilla webthings gateway addon add-on',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=requirements,
)
