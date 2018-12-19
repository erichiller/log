""" Useful auxilliary functions for logging """
import logging
import copy
import sys
import os
from typing import Dict, cast, Union

from lib.log.logger import Log
from lib.log import LogContext, Level, ElasticLogHandler, DynamicLogFormatter
from .default_config import LogConfig as config
from .private import QuietFileHandler
from lib.common import get_make_path


def getLogger(name=None) -> Log:
    """ Re-export getLogger """
    return cast(Log, logging.getLogger(name))



trace    = getLogger(config.DEFAULT_LOGGER_NAME).tracef
debug    = getLogger(config.DEFAULT_LOGGER_NAME).debugf
info     = getLogger(config.DEFAULT_LOGGER_NAME).infof
notice   = getLogger(config.DEFAULT_LOGGER_NAME).noticef
warning  = getLogger(config.DEFAULT_LOGGER_NAME).warningf
error    = getLogger(config.DEFAULT_LOGGER_NAME).errorf

log      = getLogger(config.DEFAULT_LOGGER_NAME).logf

prompt_continue = getLogger(config.DEFAULT_LOGGER_NAME).prompt_continue


def display_level_status(logger: logging.Logger):
    """ Visually print enabled levels """
    for level in (Level.TRACE, Level.DEBUG, Level.INFO, Level.NOTICE, Level.WARNING, Level.CRITICAL):
        logger.log(msg=f"log messages of level {level} are enabled", level=level, location=True)



def progress(complete, total, char_width=DynamicLogFormatter.context_marker_width):
    """ Create dynmaically updating progress bar """
    to_check = ( complete, total, char_width )
    if not all( type(i) is int for i in to_check):
        raise TypeError(f"all inputs must be of type int, {to_check}")
    complete = complete + 1
    to_check = ( complete, total, char_width )
    if total != 0 and char_width != 0:
        interval = total / char_width
    if any( i == 0 for i in to_check):
        raise ValueError(f"Inputs can not be 0, {to_check}")
    else:
        mod = ( interval ) % complete == 0
        percent = complete / total
        intervals = round( complete / interval)
    if mod == 0:
        print(f"{DynamicLogFormatter.ANSI_CLSML}{DynamicLogFormatter.ANSI_RSCUR} 0% [{percent:6.01%}] |{intervals * '='}" + ( " " * ( char_width - intervals ) ) +
              "| 100%", end='')
    if complete == total:
        print("... complete")



def getAllLoggers() -> Dict[str, Log]:
    """ Retrieve list of all loggers present """
    # log = getLogger(__name__).log
    # for (k, v) in logging.Logger.manager.loggerDict.items():
    #     if type(v) in ( logging.PlaceHolder, logging.Logger):
    #         log(f"{k:40} {repr(type(v)):30} {v}  ", level=Log.NOTICE)
    #     else:
    #         log(f"{k:40} {repr(type(v)):30} {v}  ")
    return logging.Logger.manager.loggerDict



@LogContext()
def ResetAllLoggers():
    """ Reset all loggers to use the same as the ROOT logger """
    loggers = copy.copy(logging.Logger.manager.loggerDict)
    for (k, v) in loggers.items():
        if type(v) in ( logging.PlaceHolder, logging.Logger):
            notice(f"DELETE:{k:40} {repr(type(v)):30} {v}  ")
            # del logging.Logger.manager.loggerDict[k]
            handlers = logging.getLogger(k).handlers
            for handler in handlers:
                log(f"removing {handler}", level=Level.NOTICE)
                logging.getLogger(k).removeHandler(handler)
            for handler in getLogger().handlers:
                debug(f"adding {handler}")
                logging.getLogger(k).addHandler(handler)
    return logging.Logger.manager.loggerDict



def configure_logging(log_file_path: str, log_console_level: int, elastic_log_host: str = None, elastic_log_index_name: str = "", color: bool=True):
    """ Set up Logging which the entire run will use """
    logger = getLogger()
    # logger must be set to lowest and handlers configure from there
    logger.setLevel(0)
    dyn_console           = logging.StreamHandler(sys.stdout)
    dyn_console.formatter = DynamicLogFormatter(color)
    dyn_console.setLevel(log_console_level)

    if not os.path.isdir(get_make_path(os.path.dirname(log_file_path))):
        raise FileNotFoundError(f"Can not create the FileHandler for logging at {log_file_path}, most likely the parent directory does not exist")
    log_file                = QuietFileHandler(log_file_path)
    log_file.formatter      = DynamicLogFormatter()
    # Setting to 0, send EVERYTHING to the file
    log_file.setLevel(0)

    # Log to ElasticSearch
    if elastic_log_host is not None:
        log_elastic                = ElasticLogHandler(elastic_log_host, elastic_log_index_name)
        # Setting to 0, send EVERYTHING to the ElasticSearch
        log_elastic.setLevel(0)
        logger.addHandler(log_elastic)

    logger.addHandler(dyn_console)
    logger.addHandler(log_file)
    # Configure associated modules's logging:
    # quiet these modules down
    getLogger("urllib3").setLevel(Level.WARNING)
    logger.log(level=0, msg= f"urllib3 logger level set to {Level.WARNING}")
    getLogger("matplotlib").setLevel(Level.WARNING)
    logger.log(level=0, msg=f"matplotlib logger level set to {Level.WARNING}")
    ####################
    #### Tensorflow ####
    ####################
    # turn off its build in C logging which can't be sent to python logging anyways
    # This turns off TensorFlow's noise about AVX instruction sets not being compiled in
    os.environ['TF_CPP_MIN_VLOG_LEVEL'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL']  = '0'
    getLogger('tensorflow').setLevel(Level.WARNING)
    info(f"logging configured [console level={logging.getLevelName(log_console_level)}]")



def _log_console_level(level: Union[int, Level]=None, set_handler_type=logging.StreamHandler) -> Level:
    """ Log level for Root Console """
    if isinstance(level, int ):
        for handler in getLogger().handlers:
            if type(handler) == set_handler_type:
                log(f"setting handler type{set_handler_type.__name__} to level {level}", Level.TRACE)
                handler.setLevel(level)
        log(f"Log level is now {getLogger().handlers[0].level}, root logger is at level {getLogger().level}", Level.DEBUG)
    elif level is not None:
        raise TypeError("level must be of type int")
    return Level(getLogger().handlers[0].level)



def log_check_formatting(logger=None, debug=False):
    """ # print out log levels and what color they should be in """
    def print_line(level_name, level_num, color_set="", key=None):
        print(f">>\t{color_set}Showing text printed to the console in the given ANSI values for level {level_name} ({level_num}) (key={key}) {DynamicLogFormatter.ANSI_CLEAR}")
    ansi_values = { key: getattr(DynamicLogFormatter, key) for key in dir(DynamicLogFormatter) if 'ansi_'.lower() in key.lower() }
    if logger is None:
        logger = getLogger(__name__)
    print(f"{' log_check_formatting ':=^80}")
    print(f"Evaluating logger {logger}")
    print(f"current effective level for the logger is: {logging.getLevelName(logger.getEffectiveLevel())} ({logger.getEffectiveLevel()})")
    if debug: print(ansi_values)
    for level_num, level_name in Level._level_dict.items():
        print(f"\n{'*' * 10} #{level_num:3}: {level_name} {'*' * 10}")
        if hasattr(logger, level_name.lower()):
            if debug: print(f"**Log hasattr {level_name.lower()}**")
            level_ansi = { key: getattr(DynamicLogFormatter, key) for key in dir(DynamicLogFormatter) if level_name.lower() in key.lower() }
            level_color_str = []
            if debug: print(f"{len(level_ansi)} color values found for level {level_name} ({level_num})")
            if len(level_ansi) > 0:
                if len(level_ansi) > 1:
                    print(f"multiple color values ({len(level_ansi)}; {level_ansi.keys()}) found for level {level_name} ({level_num})")
                if debug: print(f"Found ansi color which matches level({level_name.lower()}): level_ansi={type(level_ansi)}, {len(level_ansi)} {level_ansi}")
                for key, color_set in level_ansi.items():
                    print_line(level_name, level_num, color_set, key)
                level_ansi = "".join(level_ansi.values())     # just in case more than one color is found, print them all out.
                level_ansi = level_ansi.split("\u001b")
                if len(level_ansi) > 0:
                    # remove the first one, it is blank
                    level_ansi = level_ansi[1:]
                if debug: print(f"(split & remove first)\nlevel_ansi={type(level_ansi)}, {len(level_ansi)} {level_ansi}")
            else:
                print(f"#\tNo color is defined for level of {level_name} ({level_num})")
                print_line(level_name, level_num)
            for color in level_ansi:
                if debug: print(f"checking for color key for value={type(color)}, {len(color)} {color}")
                for key, value in ansi_values.items():
                    if color.lower() in value.lower():
                        level_color_str.append(key)
            ", ".join(level_color_str)
            getattr(logger, level_name.lower())(f"Displaying level {level_name} ({level_num}) in color {level_color_str}")
        else:
            print(f"!!\tNo output function `Log.<level>()` defined for level of {level_name} ({level_num})")
