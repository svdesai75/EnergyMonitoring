#!/usr/bin/env python
import sys

logFile=sys.stdout
logLevels=["debug","info","warn","error"]
logLevel="debug"

def printLevel(messageLevel):
    messageLevel=logLevels.index(messageLevel)
    threshold=logLevels.index(logLevel)
    return messageLevel >= threshold

def printMessage(message):
    logFile.write(message)
    logFile.write("\n")

def debug(message):
    if printLevel("debug"): printMessage(message)

def info(message):
    if printLevel("info"): printMessage(message)

def warn(message):
    if printLevel("warn"): printMessage(message)

def error(message):
    if printLevel("error"): printMessage(message)
