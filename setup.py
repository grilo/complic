#!/usr/bin/env python

"""
    Complic - Compliance and License discovery and reporting.
"""

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="complic",
    version="0.1",
    author="Joao Grilo",
    author_email="joao.grilo@gmail.com",
    description="Detects software licenses being used.",
    license="BSD",
    keywords="compliance license spdx",
    url="https://github.com/grilo/complic",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        'console_scripts': [
            'complic=complic.cli:main',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pylint', 'pytest', 'pytest-cov', 'pytest-mock'],
    package_data = {
        '': ['*.json'],
    },    
)
