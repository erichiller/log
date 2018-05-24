""" Define handlers """
import logging
import json
import http.client


class ElasticLogHandler(logging.Handler):
    """ ElasticLogHandler is specialized to log to ElasticSearch

    Heavily modified from HTTPHandler for json conversion of the log record.
    See HTTPHandler
    https://docs.python.org/3.6/library/logging.handlers.html#logging.handlers.HTTPHandler
    https://github.com/python/cpython/blob/3.6/Lib/logging/handlers.py#L1126
    """

    def __init__(self, host, index_name: str = "", secure: bool = False, credentials = None, context = None):
        """ Initialize the instance with the host, and optional secure (https) flag and credentials """
        logging.Handler.__init__(self)
        self.host = host
        self.index_name = index_name
        self.secure = secure
        self.credentials = credentials
        self.context = context

    def emit(self, record: logging.LogRecord):
        """ Emit (send) a json serialized version of LogRecord to Elastic Host """
        try:
            host = self.host
            if self.secure:
                h = http.client.HTTPSConnection(host, context=self.context)
            else:
                h = http.client.HTTPConnection(host)

            h.putrequest("POST", "/")

            # perform and parsing/filtering of record here
            # could restore mapLogRecord
            if isinstance(record.args, dict):
                record_args = record.args
            elif isinstance(record.args, tuple):
                record_args = dict(map(reversed, record.args))
            else:
                record_args = { "Log Args": record.args }

            try:
                log_data = {
                    "name": record.name,
                    "msg": record.msg,
                    "args": record.args,
                    "levelname": record.levelname,
                    "levelno": record.levelno,
                    "pathname": record.pathname,
                    "filename": record.filename,
                    "module": record.module,
                    # for exception info, if I really need it, I could write a custom decoder, see the default= below
                    # https://docs.python.org/3/library/json.html#basic-usage
                    # "exc_info": record.exc_info,
                    "exc_text": record.exc_text,
                    "stack_info": record.stack_info,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "created": record.created,
                    "msecs": record.msecs,
                    "relativeCreated": record.relativeCreated,
                    "thread": record.thread,
                    "threadName": record.threadName,
                    "processName": record.processName,
                    "process": record.process,
                }

                data = json.dumps({ **{ "index_suffix": self.index_name }, **log_data, **record_args }, skipkeys=True, default=lambda x: "err." )
            except Exception:
                raise ValueError(f"object unable to be encoded in ElasticLogEncoder: (index_name) (log_data) (record_args)", self.index_name, log_data, record_args)

            # support multiple hosts on one IP address...
            # need to strip optional :port from host, if present
            i = host.find(":")
            if i >= 0:
                host = host[:i]
                h.putheader("Content-type",
                            "application/json")
                h.putheader("Content-length", str(len(data)))
            else:
                raise ValueError(f"host value of {host} for ElasticLogHandler is invalid")
            if self.credentials:
                import base64
                s = ('%s:%s' % self.credentials).encode('utf-8')
                s = 'Basic ' + base64.b64encode(s).strip().decode('ascii')
                h.putheader('Authorization', s)
            h.endheaders()
            h.send(data.encode('utf-8'))
            response = h.getresponse()
            # Response Codes
            # https://docs.python.org/3/library/http.html#http-status-codes
            if response.status not in [ 200, 201, 202 ]:
                raise ConnectionError(f"When logging to ElasticHost {host} an invalid response was received {response.status}")
        except Exception:
            raise Exception("Error processing record in ElasticLogFormatter, record:", record)
