#!/usr/bin/env python3

import os
from setuptools import setup

setup(
    name="doxec",
    version= "0.2.0",
    author="Frank Sauerburger",
    author_email= "frank@sauerburger.com",
    description=("Run documentation and test whether the examples work."),
    install_requires=["argparse"],
    license="MIT",
    packages=['doxec'],
    scripts=['bin/doxec'],
    test_suite='doxec.tests',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Documentation",
        "Topic :: Education :: Testing",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Interpreters",
    ]
)
