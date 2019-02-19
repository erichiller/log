""" Shared datatypes amongst the log submodule """

import sys
import os
from logging import FileHandler
from typing import Union
from enum import Enum, unique


@unique
class LogContextStatus(Enum):
    """ LogContextStatus defines LogContext states """

    OPENING   = 1
    CURRENT   = 2
    CLOSING   = 3
    NOCONTEXT = False


class QuietFileHandler(FileHandler):
    """ Overload FileHandler's annoying behavior of not raising Exceptions """

    def handleError(self, record) -> None:
        """ Remove all action """
        pass


class DEBUG_FLAG:
    """ Container for module level debug flags """

    __MASTER               = False
    LOGGER_CONTEXT_CLOSING = __MASTER
    LOGGER_CONTEXT_OPENING = __MASTER
    CONTEXT_EXIT           = __MASTER
    CONTEXT_ENTER          = __MASTER
    CONTEXT_ETC            = __MASTER



def logging_error(msg: Union[str, TypeError, AssertionError]) -> None:
    """ Log an error for the Logger itself, output this via an alternate method """
    # TODO: make this do something real
    print(f"LOG ERROR (log_error): {msg}")
    with open(os.path.join(os.environ['HOME'], 'logging_errors.log'), 'a') as f:
        f.writelines(f"LOG ERROR (log_error): {msg}")



def _supports_ansi() -> bool:
    """ Return True if the running system's terminal supports color, and False otherwise. (from django) """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


ANSI_CAPABLE = _supports_ansi()
