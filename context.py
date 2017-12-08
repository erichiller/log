""" Defines logging.LogContext """
import logging
from types import MethodType

from lib.common import ContextDecorator
from .private import LogContextStatus
from .logger import Log
from .default_config import LogConfig as config


class LogContext(ContextDecorator):
    """ LogContext defines a contextual wrapper which logically (and graphically) wraps similar logs """

    def __init__(self, logger=None, title=None, level=None, handler=None, close=True):
        """ Initialize LogContext, allows passing of alternate parameters:

        :param logger:  alternate logger
        :param title:   title is a title for this context specifically
        :param level:   alternate default level
        :param handler: additional handler to use (will be ADDED to existing handlers
        :param close: whether or not to close the handler at context close. Default is True.
        """
        if type(logger) is MethodType:
            self.logger  = logger.__self__
        # elif type(logger) is Log:
        elif isinstance(logger, logging.Logger):
            self.logger  = logger
        else:
            self.logger  = logging.getLogger(config.DEFAULT_LOGGER_NAME)
        self.title   = title
        self.level   = level
        self.handler = handler
        self.close   = close

    def __enter__(self):
        """ Enter context """
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
        if self.handler:
            self.logger.addHandler(self.handler)
        if type(self.logger) is Log:
            self.logger.setContextStatus(LogContextStatus.OPENING)
            self.logger.setTitle(self.title)

    def __exit__(self, typeof, value, traceback):
        """ Exit context, close handlers if present """
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()
        if type(self.logger) is Log:
            self.logger.setContextStatus(LogContextStatus.CLOSING)
            self.logger.setTitle(False)
        # implicit return of None => don't swallow exceptions
