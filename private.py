""" Shared datatypes amongst the log submodule """

from enum import Enum, unique


@unique
class LogContextStatus(Enum):
    """ LogContextStatus defines LogContext states """

    OPENING   = 1
    CURRENT   = 2
    CLOSING   = 3
    NOCONTEXT = False
