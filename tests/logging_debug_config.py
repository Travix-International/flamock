import sys
import logging

logging_format = '[%(asctime)s][%(funcName)s][%(lineno)d][%(levelname)s] %(message)s'
logging.basicConfig(filename="debug.log", level=logging.DEBUG, format=logging_format, filemode='w')
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(log_handler)