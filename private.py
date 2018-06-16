""" Shared datatypes amongst the log submodule """

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
