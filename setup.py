"""A setuptools based setup module."""

from setuptools import setup, find_packages
from codecs import open
from os import path
import subprocess
import sys


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Pull in the schemas
subprocess.run(
    'git submodule init && git submodule update',
    shell=True,
    cwd=here,
    check=True,
)

requirements = [
    'jsonschema==3.2.0',
    'singleton-decorator==1.0.0',
    'websocket-client==0.57.0',
]

setup(
    name='gateway_addon',
    version='0.11.0',
    description='Bindings for Mozilla WebThings Gateway add-ons',
    long_description=long_description,
    url='https://github.com/mozilla-iot/gateway-addon-python',
    author='Mozilla IoT',
    keywords='mozilla webthings gateway addon add-on',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['schema/schema.json', 'schema/**/*.json']},
    install_requires=requirements,
)
