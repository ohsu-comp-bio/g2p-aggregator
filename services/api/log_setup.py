#!/usr/bin/python
# -*- encoding: utf-8 -*-

import logging
import sys

# customize for your needs


def init_logging():
    # # turn on max debugging
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    # formatter = logging.Formatter(
    #             '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(ch)
    logging.getLogger('').setLevel(logging.INFO)
    # # allow printing of POST body as well.
    # import httplib  # noqa
    # httplib.HTTPConnection.debuglevel = logging.DEBUG
    # logging.getLogger("urllib3").setLevel(logging.DEBUG)
