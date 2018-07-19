""" Defines logging.LogContext """
import logging
from types import MethodType
from typing import Union, Tuple, Optional
import inspect

from lib.common import ContextDecorator, Multiton
from .private import LogContextStatus, DEBUG_FLAG




class LogContext(ContextDecorator, Multiton):
    """ LogContext defines a contextual wrapper which logically (and graphically) wraps similar logs """

    _instances: dict = {}

    # previously this was set to the logcontexts level, which meant it ALWAYS printed.
    heading_level = logging.INFO

    def __init__(self,
                 logger: logging.Logger = None,
                 title: Union[str, bool, None] = None,
                 heading: Union[str, bool] = True,
                 level: int = None,
                 handler: logging.Handler = None,
                 close: bool = True) -> None:
        """ Initialize LogContext, allows passing of alternate parameters

        Parameters
        ----------
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

        Attributes
        ----------
        context_count   : int
            the number of log messages output by this logger
            this determines whether a block should ever be output
            to enclose its contents/messages

        """
        # obj_idx is set when Multion creates it (it is already set here, this is just a type hint)

        self.obj_idx: str
        self.calling_module, self.calling_class, self.wrapped_function, _, _ = LogContext.getCallingFunction()
        if type(logger) is MethodType:
            self.logger  = logger.__self__  # type: Log
        elif isinstance(logger, logging.Logger):
            self.logger  = logger  # type: Log
        else:
            self.logger  = logging.getLogger(self.calling_module)  # type: Log
        if title is None:
            self.title = None
        elif type(title) is str:
            self.title   = title
        elif title is True:
            self.title = self.getDefaultTitle()
        self.level              = level
        self.handler            = handler
        self.close              = close
        self.heading            = heading
        self.context_count: int = 0


    def __enter__(self):
        """ Enter context """
        local_debug = DEBUG_FLAG.CONTEXT_ENTER
        if local_debug is True: print(f"_______enter {self.obj_idx}, logger context={GlobalLogContext.status} [", end="")
        # test for valid Logger type
        if not hasattr(self.logger, "trace"):
            raise TypeError("LogContext's logger attribute must be of type Log")
        if self.level is not None:

            if local_debug is True:
                print(f"LogContext.title={self.title}")
                print(self.level)
                print(self.logger)
            self.old_level = self.logger.level
            self.logger.setLevel(self.level)
            if local_debug is True: print(f"level now set to {self.level} for {self.logger}")
        if self.handler:
            if self.handler not in self.logger.handlers:
                self.logger.addHandler(self.handler)
        if hasattr(self, 'title'):
            self.logger.setTitle(self.title)
        if type(GlobalLogContext.context_current) is not LogContext or (type(GlobalLogContext.context_current) is LogContext and GlobalLogContext.context_current.obj_idx != self.obj_idx):
            if local_debug is True: print("setting context_pending to self ", end="")
            GlobalLogContext.context_pending = self
            if type(GlobalLogContext.context_current) is LogContext:
                GlobalLogContext.status = LogContextStatus.CLOSING
        if type(GlobalLogContext.context_current) is LogContext and GlobalLogContext.context_current.obj_idx == self.obj_idx and GlobalLogContext.status == LogContextStatus.CLOSING:
            GlobalLogContext.status = LogContextStatus.CURRENT
        if local_debug is True: print("]")


    def __exit__(self, typeof, value, traceback):
        """ Exit context, close handlers if present

        Set CLOSING context on the logger.
        """
        local_debug = DEBUG_FLAG.CONTEXT_EXIT
        ## make a callback?
        if local_debug is True: print(f"_______exit {self.title}_______ [ ", end="")
        if not hasattr(self.logger, "trace"):
            raise TypeError("LogContext logger attribute must be of type Log")
        if self.level is not None:
            if local_debug is True: print(f"__exit__ {self.title} on {self.logger} ; level {self.level} -> {self.old_level}")
            self.logger.setLevel(self.old_level)
        if hasattr(self, 'title') and self.title is not None:
            if local_debug is True: print("++ unset title ++ ", end="")
            self.logger.setTitle(None)
        if self.handler:
            self.logger.removeHandler(self.handler)
        if self.handler and self.close:
            self.handler.close()
        if self.context_count > 0:
            self.logger.setContextStatus(LogContextStatus.CLOSING)
            if local_debug is True: print("context set to CLOSING", end="")
        else:
            if local_debug is True: print(f"no logging messages while under this context {self.title} ", end="")
        if local_debug is True: print("]")
        self.context_count = 0
        # implicit return of None => don't swallow exceptions

    def getDefaultTitle(self) -> Union[str, bool]:
        """ Return default title to use for Heading or Title if they were set to True """
        if self.wrapped_function:
            return f"{self.calling_class}.{self.wrapped_function}"
        else:
            return False

    def getHeading(self) -> Union[str, bool]:
        """ Return heading from one of the sources, False on all fails """
        if DEBUG_FLAG.CONTEXT_ETC is True: print(f"getHeading has been called")
        if type(self.heading) is str:
            return self.heading
        if type(self.title) is str:
            return self.title
        return self.getDefaultTitle()

    @classmethod
    def getCallingFunction(cls) -> Tuple[str, str, str, str, str]:
        """ Return calling function , which can be used for a default title

        Returns
        -------
        calling_class           : string    - class that the wrapped function belong's too
        wrapped_function        : string    - function that the LogContext is wrapping
        calling_filename        : string    - filename the wrapped_function is defined within
        wrapped_function_lineno : string    - the line number the wrapped function is defined on

        """
        #NOTE: use line func file to "ID" for @LogSingle
        #NOTE: add a new context of Logging(False) -> which is this just with level=CRTITICAL
        MAX_SEARCH_DEPTH = 5  # starts at 2, 5 means it will skip 0, 1; check 2-5
        outerframes = inspect.getouterframes(inspect.currentframe(), context=3)
        try:
            import re
            # from pprint import pprint #NOTE:KILL
            for depth in range(2, MAX_SEARCH_DEPTH):
                if len(outerframes) <= depth and hasattr(outerframes[depth], "code_context") and len(outerframes[depth].code_context) > 0:
                    # array is not long enough, get out
                    break
                wrapped_function = re.search("def\s*(\w*)\s*\(", outerframes[depth].code_context[-1] )
                if wrapped_function is not None:
                    wrapped_function = wrapped_function.group(1)
                    wrapped_function_lineno = outerframes[depth].lineno + 1
                    calling_filename = outerframes[depth].filename
                    calling_class = outerframes[depth].function
                    calling_module = inspect.getmodule(outerframes[depth].frame).__name__
                    return calling_module, calling_class, wrapped_function, calling_filename, wrapped_function_lineno
                # print(f"{'&'*70}")
                # pprint(outerframes, indent=2)
                # input("Press Enter to continue...")
                # pprint(outerframes[depth].code_context[-1])
            raise AssertionError(f"The search string was not found in {wrapped_function}")
        except (TypeError, AssertionError) as e:
            # from pprint import pprint
            # from traceback import print_tb
            # print(f"{'!'*70} -> {e}")
            # print_tb(e.__traceback__)
            # pprint(outerframes, indent=2)
            # input("Press Enter to continue...")
            return False, False, False, False, False


    @classmethod
    def getIndex(cls, **kwargs) -> str:
        """ Return unique string for object """
        calling_module, calling_class, wrapped_function, filename, wrapped_function_lineno = LogContext.getCallingFunction()
        if type(filename) is str and type(wrapped_function_lineno) in (str, int):
            return f"{filename}:{wrapped_function_lineno}"
        # return IndexError(f"Invalid types returned from `getCallingFunction()` unable to create id for LogContext")
        import pprint
        return pprint.pformat(inspect.getouterframes(inspect.currentframe(), context=3))







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

    status: LogContextStatus              = LogContextStatus.NOCONTEXT
    context_prior: Optional[LogContext]   = None
    context_current: Optional[LogContext] = None
    context_pending: Optional[LogContext] = None



