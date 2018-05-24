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

# registry for levels created
_level_dict = {}


class _LevelInt(int):
    """ Extend int for level """

    ID = None

    def __new__(cls, ID):
        cls.ID = ID
        # trace(f"add level name={cls.__name__} ID={ID}")
        logging.addLevelName(cls.__name__, cls.ID)
        _level_dict.update({cls.ID: cls.__name__})
        return super().__new__(cls, cls.ID)


class NOTSET(_LevelInt):
    """ Default level if nothing is configured, this will log ALL messages """


class TRACE(_LevelInt):
    """ Incredibly detailed level, report fine actions taken by program """


class DEBUG(_LevelInt):
    """ Detailed information for the user """


class INFO(_LevelInt):
    """ General information for the user """


class NOTICE(_LevelInt):
    """ Elevated information for the user """


class WARNING(_LevelInt):
    """ Warn about non-severe but concerning issue """


class ERROR(_LevelInt):
    """ Severe issue has occurred """


class CRITICAL(_LevelInt):
    """ Critical, system affecting issue """


NOTSET     = NOTSET(logging.NOTSET)
TRACE      = TRACE(logging.DEBUG - 5)
DEBUG      = DEBUG(logging.DEBUG)
INFO       = INFO(logging.INFO)
NOTICE     = NOTICE(logging.INFO + 5)
WARNING    = WARNING(logging.WARNING)
ERROR      = ERROR(logging.ERROR)
CRITICAL   = CRITICAL(logging.CRITICAL)




