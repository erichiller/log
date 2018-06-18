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

    def __init__(self, logger: Log = None, title: str = None, heading = True, level: int = None, handler: logging.Handler = None, close: bool = True):
        """ Initialize LogContext, allows passing of alternate parameters:

        Paramters
        ---------
        logger : Log
            Alternate logger
        title : str
            Title is a title for this context specifically
            The title will be added to every message within this context
        heading : bool | str
            defaults to False
            if:
                True and a title is input, the title will additionally be added
                    as a context-block enclosing header
                a str, the string will be the heading and the title will be disregarded
        level : logging.level | int
            Alternate default level for the Logger
            Use of this can suppress or reveal messages within this context that wouldn't otherwise
        handler : logging.Handler
            Additional handler to use (will be ADDED to existing handlers
        close : bool
            Whether or not to close the handler at context close. Default is True.
        """
        # obj_idx is set when Multion creates it (it is already set here, this is just a type hint)

        self.obj_idx: str
        if type(logger) is MethodType:
            self.logger: Log  = logger.__self__
        elif isinstance(logger, logging.Logger):
            self.logger: Log  = logger
        else:
            self.logger: Log  = logging.getLogger(self.getCallingModule())
        self.calling_class, self.wrapped_function, _, _ = LogContext.getCallingFunction()
        if title is None:
            self.title = None
        elif type(title) is str:
            self.title   = title
        elif title is True:
            self.title = self.getDefaultTitle()
        self.level   = level
        self.handler = handler
        self.close   = close
        self.heading = heading
        if heading is True:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!yesheading")


    def __enter__(self):
        """ Enter context """
        local_debug = True
        if local_debug is True: print(f"_______enter {self.obj_idx}, logger context={self.logger.context} [", end="")
        if type(self.logger) is not Log:
            raise TypeError("LogContexts logger attribute must be of type Log")
        if self.level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
        if self.handler:
            if self.handler not in self.logger.handlers:
                self.logger.addHandler(self.handler)
        if hasattr(self, 'title'):
            self.logger.setTitle(self.title)
        if type(self.logger.context_obj_current) is not LogContext or (type(self.logger.context_obj_current) is LogContext and self.logger.context_obj_current.obj_idx != self.obj_idx):
            if local_debug is True: print("setting context_obj_pending to self ", end="")
            self.logger.context_obj_pending = self
        if local_debug is True: print("]")
        

    def __exit__(self, typeof, value, traceback):
        """ Exit context, close handlers if present

        Set CLOSING context on the logger.
        """
        local_debug = True
        ## make a callback?
        if local_debug is True: print(f"_______exit {self.title}_______ [ ", end="")
        if type(self.logger) is not Log:
            raise TypeError("LogContext logger attribute must be of type Log")
        if self.level is not None:
            self.logger.setLevel(self.old_level)
        if hasattr(self, 'title') and self.title is not None:
            if local_debug is True: print("++ unset title ++ ", end="")
            self.logger.setTitle(None)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()
        if self.logger.context_count > 0:
            self.logger.setContextStatus(LogContextStatus.CLOSING)
            if local_debug is True: print("context set to CLOSING", end="")
        else:
            if local_debug is True: print(f"no logging messages while under this context {self.title} ", end="")
        if local_debug is True: print("]")
        self.logger.context_count = 0
        # implicit return of None => don't swallow exceptions

    def getDefaultTitle(self) -> str or False:
        """ Return default title to use for Heading or Title if they were set to True """
        if self.wrapped_function:
            return f"{self.calling_class}.{self.wrapped_function}"
        else:
            return False

    def getHeading(self) -> str or bool:
        """ Return heading from one of the sources, False on all fails """
        print(f"getHeading has been called")
        if type(self.heading) is str:
            return self.heading
        if type(self.title) is str:
            return self.title
        return self.getDefaultTitle()


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
        # return IndexError(f"Invalid types returned from `getCallingFunction()` unable to create id for LogContext")
        import pprint
        return pprint.pformat(inspect.getouterframes(inspect.currentframe(), context=3))



