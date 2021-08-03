from setuptools import setup, find_packages
from os import path

import pybibtex

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='pybibtex',
    version=pybibtex.__version__,

    # Description
    description=pybibtex.__doc__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='bibtex, latex, parsing',

    project_urls={
        'Bug Reports': 'https://github.com/pierre-24/pybibtex/issues',
        'Source': 'https://github.com/pierre-24/pybibtex',
    },

    url='https://github.com/pierre-24/pybibtex',
    author=pybibtex.__author__,

    # Classifiers
    classifiers=[
        'Environment :: Scientific',
        'Operating System :: OS Independent',

        # Specify the Python versions:
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    packages=find_packages(),
    python_requires='>=3.6',
    test_suite='tests',

    entry_points={
        'console_scripts': [
        ]
    },
)