"""
logging submodule

https://medium.com/@HLIBIndustry/python-logging-custom-handlers-f3ba784a9452
https://opensource.com/article/17/9/python-logging

See **logging flow**:
https://docs.python.org/3/howto/logging.html#logging-flow

And most of all, the LOGGING COOKBOOK is incredibly useful:
https://docs.python.org/3/howto/logging-cookbook.html

Existing Handlers:
https://docs.python.org/3/howto/logging.html#useful-handlers
"""



from .logger import Log, prompt_continue
from .context import LogContext
from .formatter import DynamicLogFormatter
from .utilities import getLogger, progress

from .level import TRACE, DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL

from . import level as Level

__all__ = [
    "DynamicLogFormatter", "LogContext", "Log",
    "getLogger", "progress", "prompt_continue",
    "TRACE", "DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL",
    "Level"
]

# test imports with:
# python3 -c 'from pprint import pprint; import lib.log; pprint(lib.log.__dict__)'
