#!/usr/bin/env python
import sys

log_file = sys.stdout
log_levels = ["debug", "info", "warn", "error"]
logLevel = "debug"


def print_level(message_level):
    message_level = log_levels.index(message_level)
    threshold = log_levels.index(logLevel)
    return message_level >= threshold


def print_message(message):
    log_file.write(message)
    log_file.write("\n")


def debug(message):
    if print_level("debug"):
        print_message(message)


def info(message):
    if print_level("info"):
        print_message(message)


def warn(message):
    if print_level("warn"):
        print_message(message)


def error(message):
    if print_level("error"):
        print_message(message)
