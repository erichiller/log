""" Logging levels

Container for all logging levels
Define and configure additional logging levels
https://docs.python.org/3/library/logging.html#logging-levels
CRITICAL	50
ERROR	    40
WARNING	    30
INFO	    20
DEBUG	    10
NOTSET	    0
"""

import logging



class Level(int):
    """ desc for levelEnum is here

    Attributes
    ----------
    NOTSET   : int(0)
        All messages are logged
    TRACE    : int(5)
        Very high logging level, most verbose messages
        Meant to trace atomic program activities
    DEBUG    : int(10)
        Detailed information to debug program functionality
    INFO     : int()
        General information for the user
    NOTICE   : int()
        Elevated information for the user
    WARNING  : int()
        Warn about non-severe but concerning issue
    ERROR    : int()
        Severe issue has occurred
    CRITICAL : int()
        Critical, system affecting issue

    """

    # registry for levels created
    _level_dict = {}

    ID = None

    def __new__(cls, id_name):
        """ Create Level with int as base """
        cls.ID = getattr(cls, id_name)
        # print(f"add level name={id_name} ID={cls.ID}")
        logging.addLevelName(id_name, cls.ID)
        cls._level_dict.update({cls.ID: id_name})
        return super().__new__(cls, cls.ID)

    NOTSET   = logging.NOTSET
    TRACE    = logging.DEBUG - 5
    DEBUG    = logging.DEBUG
    INFO     = logging.INFO
    NOTICE   = logging.INFO + 5
    WARNING  = logging.WARNING
    ERROR    = logging.ERROR
    CRITICAL = logging.CRITICAL


NOTSET     = Level("NOTSET")
TRACE      = Level("TRACE")
DEBUG      = Level("DEBUG")
INFO       = Level("INFO")
NOTICE     = Level("NOTICE")
WARNING    = Level("WARNING")
ERROR      = Level("ERROR")
CRITICAL   = Level("CRITICAL")
