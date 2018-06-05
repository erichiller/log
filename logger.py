""" Defines logging.Log """
import logging
import sys
import os
import traceback

from .private import LogContextStatus
from . import level as Level
from .default_config import LogConfig as config


# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame.
if hasattr(sys, 'frozen'):                                          # support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)



class Log(logging.Logger):
    """ Extend Logger """

    def __init__(self, name, level=Level.NOTSET):
        """ Pass name to Logger """
        self.context = False
        self.title = None

        logging.Logger.__init__(self, name, level)

        # Allow Log.log.<level>
        for num, name in Level._level_dict.items():
            setattr(Log.log, name, num)
            setattr(Log.info, name, num)

        # set prompt_continue logger to self
        setattr(self.prompt_continue.__func__, '__kwdefaults__', {'logger': self})


    def prompt_continue(self, exit_on_yes=False, message="Do you wish to proceed?") -> bool:
        """ Prompt user as to whether or not to continue

        exit - if exit is set, then sys.exit() is run rather than False being returned
            if exit is set, the user will be warned that an affirmative will exit
        """
        # see if user wishes to continue anyways
        exitwarn = "*** An answer of no will exit the program ***\n" if exit_on_yes else ""
        if input(f"{exitwarn}{message} (Y/N): ").lower() in "y":
            self.info("Continuing with user input")
            return True
        else:
            self.notice("Exiting on user prompt...")
            sys.exit()
        return False


    def trace(self, msg, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False):
        """ Incredibly detailed level, report fine actions taken by program

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        self.log(msg=msg, level=Level.TRACE, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    def debug(self, msg, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False, *args, **kwargs):
        """ Detailed information for the user

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        self.log(msg=msg, level=Level.DEBUG, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info, *args, **kwargs)

    def info(self, msg, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False):
        """ General information for the user

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        self.log(msg=msg, level=logging.INFO, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    def notice(self, msg, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False):
        """ Elevated information for the user

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        self.log(msg=msg, level=Level.NOTICE, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    def error(self, msg, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False):
        """ Severe issue has occurred

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        self.log(msg=msg, level=logging.ERROR, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    def warning(self, msg, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False):
        """ Warn about non-severe but concerning issue

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        self.log(msg=msg, level=logging.WARNING, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    def log(self, level=logging.INFO, msg=None, title: str=None, heading: bool=None, table: bool=False, relatime: bool=True, location: bool=False, exc_info=False, *args, **kwargs):
        """ Define Custom logger with additional arguments.

        Note: To log **OBJECTS** or other two dimensional data forms, put the data into msg, and set table = True
        """
        # correct for the **VERY** often reversed level & msg
        if not isinstance(level, int) and ( msg is None or isinstance(msg, int) ):
            if msg is None:
                msg = level
                level = logging.INFO
            else:
                _level = msg
                msg = level
                level = _level
        filename, line_number, function_name, stack_trace = self.findCaller(exc_info is not False)
        # if the title was set from setTitle
        if self.title:
            title = f"{self.title}: {title}"
        extra = {
            'title': title,
            'heading': heading,
            'table': table,
            'relatime': relatime,
            'location': location,
            'filename': filename,
            'line_number': line_number,
            'function_name': function_name,
            'stack_trace': stack_trace,
            'exc_info': self.exc_info(stack_trace),
            'context': self.context
        }
        try:
            logging.Logger.log(self, int(level), msg, {**kwargs, **extra} )
        except OSError as e:
            print(f"an OSError occurred whilst logging, turning off file handler printing to stdout instead. \nerror: {e}")
            self.removeHandler(logging.FileHandler)
        except Exception as e:
            print(f"an error occurred whilst logging, printing to stdout instead. \nerror: {e}")
        """ handle context opening to current transition now that the formatter has acted, push context to the next step """
        if self.context == LogContextStatus.OPENING:
            self.context = LogContextStatus.CURRENT
        """ handle context closing to nocontext transition  the formatter has acted, push context to the next step """
        if self.context == LogContextStatus.CLOSING:
            self.context = LogContextStatus.NOCONTEXT

    def exception(self, e: Exception, msg: str=None, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=True):
        """ Exception has occurred, report """
        self.log(msg=msg, level=logging.ERROR, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    def critical(self, msg: str=None, title: str=None, heading: bool=False, table: bool=False, relatime: bool=True, location: bool=False, exc_info=True):
        """ Exception has occurred, critical severity """
        self.log(msg=msg, level=logging.CRITICAL, title=title, heading=heading, table=table, relatime=relatime, location=location, exc_info=exc_info)

    @staticmethod
    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        """ Receive UNHANDLED Exception from sys and pass to logger """
        # https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger().critical(f"Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def exc_info(self, override_stack=False):
        """ Use override_stack to write log.py out of stacktrace

        exc_info returns (type, value, traceback)
        https://docs.python.org/3/library/sys.html#sys.exc_info
        """
        e = sys.exc_info()
        if override_stack is False:
            override_stack = e[2]
        return (e[0], e[1], override_stack)

    def setContextStatus(self, context):
        """ Set Context which will be passed to underlying formatter

        :param context: can have one of FOUR values, see LogContext
        """
        self.context = context

    def setTitle(self, title):
        """ Set Context which will be passed to underlying formatter """
        self.title = title

    def findCaller(self, stack_info: bool = False):
        """ Find the stack frame of the caller so that we can note the source file name, line number and function name.

        :param stack_info: set to True if stack info is to be returned
        """
        f = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        if stack_info is False:
            stack_trace = None
        else:
            # and remove the last 3 parts of the stack to keep log out of it.
            stack_trace = traceback.extract_stack()[:-3]
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name, stack_trace)
            break
        return rv

    # def addHandler(self, hdlr: logging.Handler, handlerName: str = None):
    #       """ maybe later add support for tagging handlers with a proper name """
    #     if
    #     pass;




    def removeHandler(self, hdlr: logging.Handler = None,  handlerClass: type = None):
        """ Iterate through all log handlers, remove if they match handlerClass type or hdlr Object """
        if handlerClass is None:
            if hdlr is None:
                raise TypeError("Log.removeHandler received neither a valid hdlr or handlerClass to remove, both equated to None")
            else:
                super().removeHandler(hdlr)
                return
        originalHandler = self.handlers
        try:
            self.handlers = [handler for handler in originalHandler if type(handler) is not handlerClass]
        except Exception as e:
            self.warning(f"handler removal failed with the error: {e}")
            pass


# Set as logger
logging.setLoggerClass(Log)
# NOTE: Set the log level of the log submodule itself to warning unless DEBUG is enabled
logging.getLogger(__package__).setLevel(Level.WARNING if not config.DEBUG_LOG_MODULE else Level.DEBUG)
# Set as exception handler - https://docs.python.org/3/library/sys.html#sys.excepthook
sys.excepthook = Log.handle_uncaught_exception
