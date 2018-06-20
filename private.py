""" Shared datatypes amongst the log submodule """

from enum import Enum, unique
from logging import FileHandler
from lib.common import Singleton


@unique
class LogContextStatus(Enum):
    """ LogContextStatus defines LogContext states """

    OPENING   = 1
    CURRENT   = 2
    CLOSING   = 3
    NOCONTEXT = False


class LogContextGlobalState(Singleton):
    """ Stores the global state of loggers

    Stores state globally to allow state persistence
    as log activity passes from logger to logger depending on code
    location and activities

    Attributes
    ----------
    status          : LogContextStatus
        Current global state of loggers
    context_prior   : LogContext
        Previous LogContext object, used to
        close out activity once the first message of a new context begins
    context_current : LogContext
        Active LogContext object
    context_pending : LogContext
        Context which will be active with the next log message
    context_count   : int
        the number of log messages output by this logger
        this determines whether a block should ever be output
        to enclose its contents/messages

    """

    status: LogContextStatus    = LogContextStatus.NOCONTEXT
    context_prior               = None
    context_current             = None
    context_pending             = None
    context_count: int          = 0



class QuietFileHandler(FileHandler):
    """ Overload FileHandler's annoying behavior of not raising Exceptions """

    def handleError(self, record):
        """ Remove all action """
        pass
