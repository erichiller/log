""" Custom logger for better formatting and future remote logging ease

# Formatter Objects:
Base logging.Formatter: https://docs.python.org/3/library/logging.html#formatter-objects

## Attribute:
- logging.Formatter.converter ==> convert timestamp (seconds) into formatted text, must match signature of time.localtime([secs])

## Formatter Methods
- format(record) ; complete
- formatTime(record, datefmt=None) ;; not going to override as I am not using asctime
- formatException(exc_info) ;; not going to override, I currently do this with calling anything in format()
- formatStack(stack_info) ; complete


# Formatting and Tracebacks:
from __dir__() of FrameSummary:
- 'line'
- 'filename',
- 'lineno',
- 'locals',
- 'name'


"""
import pprint
import os
import traceback
import logging

from lib.common import property_lazy_static

from .private import LogContextStatus
from lib.log import Level
from .default_config import LogConfig as config



class LogFormatException(SyntaxError):
    """ Exception for Log Formatter Errors """

    pass


class DynamicLogFormatter(logging.Formatter):
    """ Return a dynamic message dependent upon the level """

    output_width             = 250
    column_name_width        = 50
    context_marker_width     = 120
    """
    https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    ANSI_CLEAR               = "\u001b[0m"
    ANSI_CLEOL               = "\u001b[K"                           # CLEAR TO END OF LINE
    ANSI_CLSML               = "\u001b[1K"                          # CLEAR SAME LINE
    ANSI_RSCUR               = "\u001b[G"                           # RESET / MOVE the CURSOR to the line beginning

    ANSI_BLACK               = "\u001b[30m"
    ANSI_RED                 = "\u001b[31m"
    ANSI_GREEN               = "\u001b[32m"
    ANSI_YELLOW              = "\u001b[33m"
    ANSI_BLUE                = "\u001b[34m"
    ANSI_MAGENTA             = "\u001b[35m"
    ANSI_CYAN                = "\u001b[36m"
    ANSI_WHITE               = "\u001b[37m"

    ANSI_BG_BLACK            = "\u001b[40m"
    ANSI_BG_RED              = "\u001b[41m"
    ANSI_BG_GREEN            = "\u001b[42m"
    ANSI_BG_YELLOW           = "\u001b[43m"
    ANSI_BG_BLUE             = "\u001b[44m"
    ANSI_BG_MAGENTA          = "\u001b[45m"
    ANSI_BG_CYAN             = "\u001b[46m"
    ANSI_BG_WHITE            = "\u001b[47m"

    COLOR_LOCATION           = f"{ANSI_BLACK}{ANSI_BG_WHITE}"
    COLOR_TRACE              = ANSI_WHITE
    COLOR_DEBUG              = ANSI_MAGENTA
    COLOR_NOTICE             = f"{ANSI_BLACK}{ANSI_BG_YELLOW}"
    COLOR_WARNING            = ANSI_RED
    COLOR_CRITICAL           = f"{ANSI_RED}{ANSI_BG_WHITE}"
    COLOR_HIGHLIGHT_CRITICAL = f"{ANSI_WHITE}{ANSI_BG_RED}"

    COLOR_LOCAL_FRAME        = f"{ANSI_BG_YELLOW}{ANSI_BLACK}"
    COLOR_EXTERNAL_FRAME     = f"{ANSI_BG_BLACK}{ANSI_WHITE}"
    COLOR_FINAL_FRAME        = f"{ANSI_WHITE}{ANSI_BG_RED}"

    COLOR_CONTEXT_MARKER     = ANSI_GREEN

    COLOR_DEFAULT            = ANSI_CYAN

    def __init__(self, color: bool = False):
        """ Init Formatter, provide color=True if ANSI color output is desired

        NOTE: this does not honor the standard Formatter interface: https://docs.python.org/3/howto/logging.html#formatters
        signature should be __init__(fmt=None, datefmt=None, style='%')
        """
        self.color = color
        self.clear = DynamicLogFormatter.ANSI_CLEAR if color is True else ""
        self.eol   = DynamicLogFormatter.ANSI_CLEOL if color is True else ""

    @property_lazy_static
    def local_module_base(cls) -> str:
        """ Guess what the local module base path is for cancelling out unnecassry prints """
        # going to be simplistic and just do up 2 levels.
        return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".." ))

    def format(self, record: logging.LogRecord) -> str:
        """ Format message Object (via attributes of LogRecord) of unknown type into printable and easily readable string

        https://docs.python.org/3/library/logging.html#logging.LogRecord
        https://docs.python.org/3/library/logging.html#logrecord-attributes
        NOTE: record.getMessage() will ALWAYS return a str()
                for the actual object the user provided use `record.msg`
        """
        level_print     = str()
        prepend         = str()
        prependtime     = str()
        output          = record.msg if hasattr(record, "msg") else str()
        location        = str()
        highlight_color = str()
        heading         = record.args['heading'] if 'heading' in record.args and record.args['heading'] is not False else False
        title           = heading if heading is not False and type(heading) is str else str()
        # if there are newlines in the output, make it a block.
        if repr(output).count("\n") > 1:
            heading = True
        # typically closing is done in the same log message as heading
        # but this is disabled when in context
        closing         = heading
        context_marker  = str()
        context         = record.args['context'] if 'context' in record.args and record.args['context'] in (LogContextStatus.OPENING, LogContextStatus.CURRENT, LogContextStatus.CLOSING) else False
        clear           = self.clear
        eol             = self.eol
        relatime        = record.args["relatime"]    if 'relatime'    in record.args else False
        stack_trace     = record.args['stack_trace'] if "stack_trace" in record.args and type(record.args['stack_trace']) is list else False
        flag_location   = record.args["location"]    if 'location'    in record.args else False
        table           = record.args["table"]       if 'table'       in record.args else False

        try:
            if isinstance( output, str ):
                pass
            elif table:
                iterate_source = output
                output = str()
                if isinstance(iterate_source, dict):
                    iterate_source = iterate_source.items()
                try:
                    iterate_source = iter(iterate_source)
                    for d in iterate_source:
                        output += self.make_row(*d)
                except TypeError:
                    # raise TypeError("Best handled elsewhere: you requested a table, but this isn't iterable")
                    output += repr(output)
            else:
                raise TypeError("Best handled elsewhere: this is neither a table, nor a string")
        except TypeError:
            """ when the object is not a string """
            output = pprint.pformat(output, width=self.output_width, indent=4)

        if record.levelno == logging.WARNING:                                   # add levelname
            level_print = f"{record.levelname} "
        if record.levelno == logging.CRITICAL:                                  # add levelname
            level_print = f"{record.levelname} "
            highlight_color = self.COLOR_HIGHLIGHT_CRITICAL if self.color else ""

        if logging.getLogger(__name__).getEffectiveLevel() <= Level.DEBUG:
            # NOTE: THIS IS VERY LENGTHY LOGGING
            print(f"args={record.args}")
            print(f"exc_info={record.exc_info}")
            print(f"filename={record.filename}")
            print(f"funcName={record.funcName}")
            print(f"lineno={record.lineno}")
            print(f"pathname={record.pathname}")
            print(f"stack_info={record.stack_info}")
            print(f"flag_location={flag_location}")
            print(f"---- exc_info[3] {type(record.exc_info[2])}--->")
            print( traceback.extract_tb(record.exc_info[2]) )
        # https://docs.python.org/3/library/traceback.html#module-traceback
        if record.levelno == logging.CRITICAL and type(record.exc_info) is tuple and type(record.exc_info[2]) is not None:
            trace = traceback.extract_tb(record.exc_info[2])
            last = trace[len(trace) - 1]
            if logging.getLogger(__name__).getEffectiveLevel() <= Level.DEBUG:
                # NOTE: THIS IS VERY LENGTHY LOGGING
                print(f"lineno={last.lineno}")
                print(f"filename={last.filename}")
                print(f"name={last.name}")

            record.lineno = last.lineno
            record.pathname = last.filename
            record.funcName = last.name
            title = output
            relatime = True
            output = f"{record.exc_info[1]} {repr(record.exc_info[0])}"
            stack_trace = trace

        if stack_trace is not False:
            output += f"\n{clear}" + self.formatStack(stack_trace).replace("\n", f"\n{clear}{' '*len(prependtime)}").rstrip(f"\n{clear}") + f"{eol}{clear}"

        if relatime is True:                                                    # add relative timestamp
            s = record.relativeCreated // 1000
            m = f"{int(s // 60 % 60):0>2}m" if s >= 60 else ""
            h = str(int(s // 3600)) + "h" if s >= 3600 else ""
            s = str(int(s % 60)) + "s"
            prependtime = f"[{h:>4} {m} {s:0>3}] "

        """ handle context """
        if context:
            if context == LogContextStatus.OPENING:
                context_marker = self.COLOR_CONTEXT_MARKER + f" START {title} ".center(self.context_marker_width, ">") + f"{clear}"
                closing = heading = False

            elif context == LogContextStatus.CURRENT:
                # NOTE(erichiller) UNSURE OF WHAT TO DO WITH PREPEND RIGHT NOW
                # prepend   = "\t"
                # prepend = "↳"
                closing = heading = False
            elif context == LogContextStatus.CLOSING:
                closing = heading = False
                context_marker = self.COLOR_CONTEXT_MARKER + f" END {title} ".center(self.context_marker_width, "<") + f"{clear}"
            if record.msg is None:
                return context_marker

        if 'title' in record.args and record.args['title'] not in (None, False):  # add user provided title
            title = f" {record.args['title']} {title}"
        if closing:
            output = ( f"{output}" + "\n" +                                   # add an END OF BLOCK marker
                       f" END {title} ".center(self.column_name_width, "<") )
        if heading is not False:                                              # this has been marked as a heading so give it some flourish
            title = title.center(self.column_name_width - len(prepend), '>' ) + "\n"

        # determine color level, Python has no switch statement
        if record.levelno >= Level.CRITICAL:                                    # set color
            color = self.COLOR_CRITICAL
            flag_location = True
        elif record.levelno >= Level.WARNING:                                   # set color
            color = self.COLOR_WARNING
            flag_location = True
        elif record.levelno >= Level.NOTICE:
            color = self.COLOR_NOTICE
        elif record.levelno == Level.DEBUG:
            color = self.COLOR_DEBUG
        elif record.levelno == Level.TRACE:
            color = self.COLOR_TRACE
        else:
            color = self.COLOR_DEFAULT

        if level_print != "":
            title = (level_print + title).ljust(                                # add level
                self.column_name_width - len(prepend) - len(prependtime))
        if title != "" and title[-1] != "\n":
            title = title + ": "
        if len(title) > 0 and title[0].isspace():                               # strip any whitespace on left
            title = title.lstrip()
            if ":" in title:                                                    # run a check just to see if it should be added back in
                title = "".join(title.rsplit(":", 1)).ljust(self.column_name_width - len(prepend) - len(prependtime))
                title = title + ": "
        if flag_location:
            location_color = self.COLOR_LOCATION if self.color else ""
            location = location_color + self.caller_location_string(record) + f"{eol}\n{clear}"
        if self.color is False: eol = color = clear = ""
        highlight_color = color if highlight_color == "" else highlight_color
        # used below llne purely for debugging what was my logs and what wasn't
        # else: color = f"{self.ANSI_BG_MAGENTA}{color}"
        return context_marker + f"{color}{prependtime}{location}{highlight_color}{prepend}{title}{clear}{color}{output}{eol}{clear}".replace(f"\n{clear}", f"{eol}{clear}\n").replace("\n", f"\n{' ' * len(prependtime)}")

    def highlightTextOnly(self, text, color) -> str:
        """ Highlight only text; trim """
        if self.color:
            color = color
            #### reverse search #### find FIRST OCCURANCE OF NONWHITESPACE #### insert CLEAR
        else:
            color = ""
        return f"{color}{text}{self.clear}"

    def formatStack(self, stack_info) -> str:
        """ Colorize (if color is True) stack print """
        # fullfills https://docs.python.org/3/library/logging.html#logging.Formatter.formatStack
        formatStack = str()
        frames = len(stack_info)
        for i in range(frames):
            frame = stack_info[i]
            if i == frames - 1:
                color = self.COLOR_FINAL_FRAME
                prefix = ""
            elif frame.filename.startswith(self.local_module_base) or frame.filename.startswith('.'):
                color = self.COLOR_LOCAL_FRAME
                prefix = "    "
            elif not config.FORMATTER_STACK_FILTER:
                color = self.COLOR_EXTERNAL_FRAME
                prefix = "    "
            else:
                continue
            if not self.color: color = ""
            color = f"{color}"
            formatStack += color + self.caller_location_string(frame, prefix) + f"{self.eol}\n{self.clear}"
        return formatStack

    def caller_location_string(self, record, prefix: str = ">>>>") -> str:
        """ Create string representing the caller's location """
        if type(record) == traceback.FrameSummary:
            path = record.filename
            line = record.lineno
            func = record.name
        elif hasattr(record, "pathname") and hasattr(record, "lineno") and hasattr(record, "funcName"):
            path = record.pathname
            line = record.lineno
            func = record.funcName
        elif all(k in record.args for k in ("filename", "line_number", "function_name")):
            path = record.args["filename"]
            line = record.args["line_number"]
            func = record.args["function_name"]

        if os.path.isabs(path) and os.path.splitdrive(path)[0] == os.path.splitdrive(config.BASE_PATH)[0] and os.path.commonpath([path, config.BASE_PATH]) == config.BASE_PATH:
            path = os.path.relpath(path, config.BASE_PATH)
        return f"{prefix + ' ' + path:100} , {'line # ' + str(line):12} in {func:30}"

    def make_row(self, *args)-> str:
        """ Take unlimited arguments and writes the first one as a `title` column, and alternating ones thereafter to columns of ` title | value | title | value .... ` """
        if isinstance(args[0], str):
            return args[0].ljust(self.column_name_width) + ": " + "".join(map(str, args[1:])) + "\n"
        elif isinstance(args[0], dict) and len(args) == 1:
            return self.make_row(**args[0])
        elif isinstance(repr(args[0]), str):
            return repr(args[0])
        else:
            raise LogFormatException(f"make row encountered an object that refused to be handled {args[0]}")

    def formatException(self, exc_info) -> str:
        """ Fullfills https://docs.python.org/3/library/logging.html#logging.Formatter.formatException """
        # to be completed, but this is the proper signature
        exception_str = "nothing here; Eric fill this in"
        return exception_str
