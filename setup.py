#!/usr/bin/env python

import sys
from setuptools import setup

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name = 'loghog',
    version = '3',
    description = 'LogHog python client',
    author_email = 'info@activefrequency.com',
    url = 'https://github.com/activefrequency/loghog',
    license = 'Apache2',
    test_suite = 'tests.tests_all',
    py_modules = ['loghog'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    **extra
)
