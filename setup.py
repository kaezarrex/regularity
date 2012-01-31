#! /usr/bin/env python

from setuptools import setup, find_packages

import regularity

requirements = list()
with open('requirements.txt', 'r') as requirements_file:
    for requirement in requirements_file:
        requirements.append(requirement)

setup(
    name='Regularity',
    version=regularity.__version__,
    description='For people who want to see how they use their time',
    author='Tim Johnson',
    packages=find_packages(),
    install_requires=requirements,
    scripts=['bin/bm', 'bin/regularityd', 'bin/regularity-api']
)
    
    
