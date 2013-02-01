#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

curdir = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.dirname(curdir)] + sys.path

import logging, time
from loghog import LoghogHandler

def setup_logging():
    logger = logging.getLogger()

    # NOTE: In order to use this example, you must generate a client certificate.
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

    handler = LoghogHandler('kitchen-sink-app',
        host='localhost',           # Default is 'localhost'
        port=5577,                  # Default is 5566. Port 5577 is usually SSL enabled
        stream=True,                # Default is True
        secret='my-big-secret',     # Specify this if the server expects it
        compression=True,           # Default is False
        hostname='example01',       # Default is determined automatiaclly
        ssl_info=ssl_info,          # Default is None for disabled SSL
        max_buffer_size=1024,       # How many messages to enque if the server is down, before dropping the oldest ones
        print_debug=True            # Default is False. Prints connection errors to STDOUT
    )

    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


setup_logging()

log = logging.getLogger()

while True:
    log.info(u"That is one hot jalapño!")
    time.sleep(1)
