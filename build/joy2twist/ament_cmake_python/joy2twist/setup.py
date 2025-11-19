from setuptools import find_packages
from setuptools import setup

setup(
    name='joy2twist',
    version='1.0.0',
    packages=find_packages(
        include=('joy2twist', 'joy2twist.*')),
)
