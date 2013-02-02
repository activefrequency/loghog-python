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

    # If the server-side specifies a secret, you must provide it here as well.
    # If a secret is specified here, all messages are signed using HMAC.
    # Any messages with invalid signatures will be ignored by the server.

    handler = LoghogHandler('app-with-secret', secret='my-big-secret')

    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


setup_logging()

log = logging.getLogger()

while True:
    log.info("That is one hot jalapño!")
    time.sleep(1)
