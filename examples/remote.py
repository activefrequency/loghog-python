#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

curdir = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.dirname(curdir)] + sys.path

import logging, time
from loghog import LoghogHandler

def setup_logging():
    logger = logging.getLogger()

    # You can log messages to a remote server. Simply specify the address parameter.
    # Don't forget to listen on the appropriate address on the server since
    # by default it only listens on localhost.
    handler = LoghogHandler('my-first-app', host='localhost', port=5566)
    
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


setup_logging()

log = logging.getLogger()

while True:
    log.info("That is one hot jalapño!")
    time.sleep(1)
