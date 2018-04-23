import logging, os
from logging.handlers import RotatingFileHandler

file_handler = False
LOG_HOME = 'log'

logger = logging.getLogger('magnet')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  
formatter = logging.Formatter('%(threadName)s %(asctime)s-%(name)s-%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def make_file_log(file = 'magnet.log'):
    global file_handler
    if not file_handler:
        if not os.path.exists(LOG_HOME):
            os.makedirs(LOG_HOME)
        handler = RotatingFileHandler(LOG_HOME + '/' + file, maxBytes = 1024 * 1024 * 100, backupCount = 10)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        file_handler = True

