#!/usr/bin/env python

from setuptools import setup

from loghog import __version__ as VERSION


setup(
    name = 'loghog',
    version = VERSION,
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
)
