""" Defines logging.LogContext """
import logging
from types import MethodType
import inspect

from lib.common import ContextDecorator, Multiton
from .private import LogContextStatus
from .logger import Log


class LogContext(ContextDecorator, Multiton):
    """ LogContext defines a contextual wrapper which logically (and graphically) wraps similar logs """

    _instances: dict = {}

    def __init__(self, logger: Log = None, title: str = None, level: int = None, handler: logging.Handler = None, close: bool = True):
        """ Initialize LogContext, allows passing of alternate parameters:

        :param logger:  alternate logger
        :param title:   title is a title for this context specifically
        :param level:   alternate default level
        :param handler: additional handler to use (will be ADDED to existing handlers
        :param close: whether or not to close the handler at context close. Default is True.
        """
        # obj_idx is set when Multion creates it (it is already set here, this is just a type hint)
        self.obj_idx: str
        if type(logger) is MethodType:
            self.logger: Log  = logger.__self__
        elif isinstance(logger, logging.Logger):
            self.logger: Log  = logger
        else:
            self.logger: Log  = logging.getLogger(self.getCallingModule())
        if title is None:
            calling_class, wrapped_function, _, _ = LogContext.getCallingFunction()
            if wrapped_function:
                self.title = f"{calling_class}.{wrapped_function}"
            else:
                self.title = None
        else:
            self.title   = title
        self.level   = level
        self.handler = handler
        self.close   = close


    def __enter__(self):
        """ Enter context """
        if type(self.logger) is not Log:
            raise TypeError("LogContexts logger attribute must be of type Log")
        if type(self.logger.contextObj) is not LogContext or (type(self.logger.contextObj) is LogContext and self.logger.contextObj.obj_idx != self.obj_idx):
            self.logger.setContextStatus(LogContextStatus.OPENING)
        self.logger.contextObj = self
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
        if self.handler:
            if self.handler not in self.logger.handlers:
                self.logger.addHandler(self.handler)
        self.logger.log(level=self.level, heading=self.title)
        self.logger.setTitle(self.title)

    def __exit__(self, typeof, value, traceback):
        """ Exit context, close handlers if present """
        if type(self.logger) is not Log:
            raise TypeError("LogContexts logger attribute must be of type Log")
        # self.logger.contextObj = None
        self.logger.setContextStatus(LogContextStatus.CLOSING)
        # self.logger.log(level=self.level)
        self.logger.setTitle(False)
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()
        # implicit return of None => don't swallow exceptions

    def getCallingModule(self):
        """ Return calling module , which is most likely to be the Logger name """
        return inspect.getmodule(inspect.stack()[-1][0]).__name__

    @classmethod
    def getCallingFunction(cls) -> (str, str, str, str):
        """ Return calling function , which can be used for a default title

        Returns
        -------
        calling_class           : string    - class that the wrapped function belong's too
        wrapped_function        : string    - function that the LogContext is wrapping
        calling_filename        : string    - filename the wrapped_function is defined within
        wrapped_function_lineno : string    - the line number the wrapped function is defined on

        """
        # curframe = inspect.currentframe()
        #NOTE: use line func file to "ID" for @LogSingle
        #NOTE: add a new contect of Logging(False) -> which is this just with level=CRTITICAL
        #NOTE: stack contexts if they are the same, do not keep printing >>>> START <<<< if same consecutie
        #NOTE: I _believe_ that the closing context is tacked to the next log message
        #           ... end this with an explicit log() call
        #           when the formatter detects LogClosingContext and a message of None
        #           ... then it just returns the Context marker.
        #NOTE: something something code context
        # calframe = inspect.getouterframes(curframe, 2)
        # print(f"calling function={calframe[-1]}")
        # print(f"calling function={calframe[-1]}")
        outerframes = inspect.getouterframes(inspect.currentframe(), context=3)
        calling_class = outerframes[-2].function
        try:
            import re
            wrapped_function = re.search("def\s*(\w*)\s*\(", outerframes[-2].code_context[-1] ).group(1)
            wrapped_function_lineno = outerframes[-2].lineno + 1
            calling_filename = outerframes[-2].filename
        except TypeError:
            return False, False, False, False
        return calling_class, wrapped_function, calling_filename, wrapped_function_lineno


    @classmethod
    def getIndex(cls, **kwargs) -> str:
        """ Return unique string for object """
        calling_class, wrapped_function, filename, wrapped_function_lineno = LogContext.getCallingFunction()
        if type(filename) is str and type(wrapped_function_lineno) in (str, int):
            return f"{filename}:{wrapped_function_lineno}"
        return IndexError(f"Invalid types returned from `getCallingFunction()` unable to create id for LogContext")



