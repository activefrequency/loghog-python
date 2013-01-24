#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

curdir = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.dirname(curdir)] + sys.path

import logging, time
from loghog import LoghogHandler

def setup_logging():
    logger = logging.getLogger()

    # Set print_debug = True to see connection errors
    handler = LoghogHandler('my-first-app', print_debug=True)

    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


setup_logging()

log = logging.getLogger()

while True:
    log.info(u"That is one hot jalapño!")
    time.sleep(1)
