#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys, os

curdir = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.dirname(curdir)] + sys.path

import logging, time
from loghog import LoghogHandler

def setup_logging():
    logger = logging.getLogger()

    # To send log messages over UDP, simply set stream=False.
    # Note that UDP has several drawbacks compared to using TCP. Specifically:
    #
    #  * Messages may be delivered out of order
    #  * Messages may be dropped
    #  * It is harder to debug any issues since packets are not explicitly rejected.
    #
    # On the other hand, sending data over UDP is master, since UDP is
    # connectionless, so there is less overhead for your application.

    handler = LoghogHandler('my-first-app', stream=False)
    
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


setup_logging()

log = logging.getLogger()

while True:
    log.info("That is one hot jalapño!")
    time.sleep(1)

