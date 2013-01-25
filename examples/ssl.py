#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

curdir = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.dirname(curdir)] + sys.path

import logging, time
from loghog import LoghogHandler

def setup_logging():
    logger = logging.getLogger()
    
    # In order to use this example, you must generate a client certificate.
    # Simply use the loghog-client-cert command on the machine that will 
    # run loghogd:
    #
    #   $ sudo loghog-client-cert `hostname`
    #
    # The above will generate a file called `hostname`.pem. Use this file with
    # your project, along with loghogd-ca.cert to encrypt all traffc between
    # your application and the server

    ssl_info = {
        'pemfile': '/PATH/TO/CLIENT.pem',
        'cacert': '/etc/loghogd/certs/loghogd-ca.cert',
    }

    handler = LoghogHandler('my-first-app', address=('localhost', 5577), ssl_info=ssl_info, print_debug=True)

    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


setup_logging()

log = logging.getLogger()

while True:
    log.info(u"That is one hot jalapño!")
    time.sleep(1)
