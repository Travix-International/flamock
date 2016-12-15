import json
import datetime
import logging


def encode_to_json_decorator(level):
    def decorator(func):
        def func_wrapper(cls, message):
            kwargs = {'ts': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
                      'level': logging.getLevelName(level),
                      'message': message}
            s = cls.encoder.encode(kwargs)
            return func(cls, s)
        return func_wrapper
    return decorator


class JsonLogging:
    """
    Class for saving log messages in JSON format
    """

    logger = logging.getLogger()
    encoder = json.JSONEncoder(sort_keys=True)

    @classmethod
    @encode_to_json_decorator(logging.DEBUG)
    def debug(cls, msg):
        cls.logger.debug(msg)

    @classmethod
    @encode_to_json_decorator(logging.INFO)
    def info(cls, msg):
        cls.logger.info(msg)

    @classmethod
    @encode_to_json_decorator(logging.WARNING)
    def warning(cls, msg):
        cls.logger.warning(msg)

    @classmethod
    @encode_to_json_decorator(logging.ERROR)
    def error(cls, msg):
        cls.logger.error(msg)

    @classmethod
    def exception(cls, msg):
        cls.logger.exception(msg)
