import json
import datetime
import logging


def encode_to_json_decorator(level):
    def decorator(func):
        def func_wrapper(self, message):
            kwargs = dict({'ts': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
                           'level': logging.getLevelName(level),
                           'message': message})
            s = self.encoder.encode(kwargs)
            return func(self, s)
        return func_wrapper
    return decorator


class JsonLogging(object):
    """
    Class for saving log messages in JSON format
    """

    logger = None
    encoder = None

    def __init__(self, logger):
        self.logger = logger
        self.encoder = json.JSONEncoder(sort_keys=True)

    @encode_to_json_decorator(logging.DEBUG)
    def debug(self, msg):
        self.logger.debug(msg)

    @encode_to_json_decorator(logging.INFO)
    def info(self, msg):
        self.logger.info(msg)

    @encode_to_json_decorator(logging.WARNING)
    def warning(self, msg):
        self.logger.warning(msg)

    @encode_to_json_decorator(logging.ERROR)
    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.exception(msg)