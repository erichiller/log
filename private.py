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


class GlobalLogContext:
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

    """

    status: LogContextStatus    = LogContextStatus.NOCONTEXT
    context_prior               = None
    context_current             = None
    context_pending             = None




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

