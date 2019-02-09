""" Shared datatypes amongst the log submodule """

from typing import Union
from enum import Enum, unique
from logging import FileHandler


@unique
class LogContextStatus(Enum):
    """ LogContextStatus defines LogContext states """

    OPENING   = 1
    CURRENT   = 2
    CLOSING   = 3
    NOCONTEXT = False


class QuietFileHandler(FileHandler):
    """ Overload FileHandler's annoying behavior of not raising Exceptions """

    def handleError(self, record):
        """ Remove all action """
        pass


class DEBUG_FLAG:
    """ Container for module level debug flags """

    __MASTER = False
    LOGGER_CONTEXT_CLOSING = __MASTER
    LOGGER_CONTEXT_OPENING = __MASTER
    CONTEXT_EXIT           = __MASTER
    CONTEXT_ENTER          = __MASTER
    CONTEXT_ETC            = __MASTER



def logging_error(msg: Union[str, TypeError, AssertionError]):
    """ Log an error for the Logger itself, output this via an alternate method """
    # TODO: make this do something real
    print(f"LOG ERROR (log_error): {msg}")

