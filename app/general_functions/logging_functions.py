#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import datetime

from ..my_config.my_config import fLoggingVars

"""
    Logging functions
"""

def fWriteLog(callId: str = None, f: str = None, message: str = None, level: str = None) -> str:
    """
    write log message to a file on the disk
    use logging levels
    - logLevelsShow - to filter log levels to be stored
    - level - to be used for the specific log
    """

    fName = fWriteLog.__name__

    logLevels = ["info", "warning", "critical", "debug"]

    try:
        myLoggingVars = fLoggingVars()
        myLogLevelsShow = myLoggingVars["myLogLevelsShow"]
        myLoggingFilePath = myLoggingVars["myLoggingFilePath"]
    except NameError:
        myLogLevelsShow = logLevels
        myLoggingFilePath = "/code/logfile.log"

    timeNow = datetime.datetime.now().isoformat()
    
    if f is None:
        f = "Unknown function"
    if level is None:
        level = "INFO"
    else:
        level = level.upper()

    # check for defined log levels
    if level.lower() in myLogLevelsShow:
        if message is not None:
            message = str(callId)+" ::: "+str(f)+" ::: "+str(level)+" ::: "+str(timeNow)+" ::: "+str(message)
            try:
                with open(myLoggingFilePath, "a+") as logFile:
                    logFile.write(message+"\n")
            except:
                pass
    
    return "OK"