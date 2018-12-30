""" ``lib.log`` submodule provides formatted logs for easier (human) consumption

Colors Generated
----------------

Exceptions
----------
When an Exception is thrown, the traceback is colored to help identify code types

* The line which raised the Exception is highlighted in red.
* Yellow lines are within non-Python/pip installed packages (typically the code you've written)
* uncolored lines are traceback entries within the Python installation directory

See Also
--------
https://medium.com/@HLIBIndustry/python-logging-custom-handlers-f3ba784a9452

https://opensource.com/article/17/9/python-logging

See `logging flow <https://docs.python.org/3/howto/logging.html#logging-flow>`

And most of all, the `LOGGING COOKBOOK`_ is incredibly useful

.. _LOGGING COOKBOOK: https://docs.python.org/3/howto/logging-cookbook.html

`Existing Handlers <https://docs.python.org/3/howto/logging.html#useful-handlers>`


Future Additions & Ideas
------------------------

In the future it would also be a nice addition to have a StructuredFormatter that output in JSON or some other structured output

def json formatter ???

https://docs.python.org/3.6/howto/logging-cookbook.html#implementing-structured-logging

"""


from lib.log.handler import ElasticLogHandler
from lib.log.level import TRACE, DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, Level
from lib.log.context import LogContext, GlobalLogContext
from lib.log.logger import Log
from lib.log.formatter import DynamicLogFormatter
from lib.log.utilities import getLogger, progress, prompt_continue


__all__ = [
    "DynamicLogFormatter", "ElasticLogHandler", "LogContext", "Log", "GlobalLogContext",
    "getLogger", "progress", "prompt_continue",
    "TRACE", "DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL",
    "Level"
]

# test imports with:
# python3 -c 'from pprint import pprint; import lib.log; pprint(lib.log.__dict__)'

