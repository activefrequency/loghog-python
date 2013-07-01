#!/usr/bin/env python

import sys
from setuptools import setup

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name = 'loghog',
    version = '0.7',
    description = 'LogHog python client',
    author = 'Active Frequency, LLC',
    author_email = 'info@activefrequency.com',
    url = 'https://github.com/activefrequency/loghog',
    license = 'Apache2',
    test_suite = 'tests.tests_all',
    py_modules = ['loghog'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
    **extra
)
