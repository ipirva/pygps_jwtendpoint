#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
    Default Variables
"""


def fLoggingVars() -> dict:
    """
        Return logging vars
    """
    variables = dict()
    # the log level accepted
    variables["myLogLevelsShow"] = ["info", "warning", "critical", "debug", "error"]
    variables["myLoggingFilePath"] = "/code/logs/logfile.log"

    return variables

def fCryptoVars() -> dict:
    """
        Return crypto vars
    """
    variables = dict()
    variables["privateKeyPath"] = "keys/key"

    return variables