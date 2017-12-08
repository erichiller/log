""" Contains basic configuration for logging functionality which can be overriden elsewhere """
import os.path
import sys


class LogConfig:
    """ Enumerate configuration """

    # Do not use the RootLogger the class has annoying differences with my logger
    DEFAULT_LOGGER_NAME = "default"

    """ Only display local frames when printing the stack, True = only local """
    FORMATTER_STACK_FILTER = False

    BASE_PATH = os.path.dirname(sys.modules['lib'].__path__[0])

    """ Set to true to log within the log submodule itself """
    DEBUG_LOG_MODULE = False

    """ default format """
    # NOTE: THIS IS CURRENTLY NOT USED
    DEFAULT_FORMAT = "%(relativeCreated)d"



