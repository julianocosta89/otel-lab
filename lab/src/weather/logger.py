#!/usr/bin/python

import logging

def initLogger(service_name):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    return logger
