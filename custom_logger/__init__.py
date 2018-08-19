from __future__ import print_function
import os
import sys
import dotenv
from pytz import utc, timezone
from datetime import datetime
import logging
import bugsnag
from bugsnag.handlers import BugsnagHandler

# Environment variables.
dotenv_path = os.path.join(os.path.dirname(__file__), './.env')
dotenv.load_dotenv(dotenv_path)
''' Base logging config '''
pacfic_timezone = timezone('America/Los_Angeles')
env = os.getenv('ENV')


def pacific_time_converter(*args):
    utc_datetime = utc.localize(datetime.utcnow())
    converted = utc_datetime.astimezone(pacfic_timezone)
    return converted.timetuple()


logging.Formatter.converter = pacific_time_converter

formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d (PDT) -- jump-booker'
    ' -- %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


class ColorStreamHandler(logging.StreamHandler):
    DEFAULT = '\x1b[0m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    CYAN = '\x1b[36m'

    CRITICAL = RED
    ERROR = RED
    WARNING = YELLOW
    INFO = GREEN
    DEBUG = CYAN

    @classmethod
    def _get_color(cls, level):
        if level >= logging.CRITICAL:
            return cls.CRITICAL
        elif level >= logging.ERROR:
            return cls.ERROR
        elif level >= logging.WARNING:
            return cls.WARNING
        elif level >= logging.INFO:
            return cls.INFO
        elif level >= logging.DEBUG:
            return cls.DEBUG
        else:
            return cls.DEFAULT

    def __init__(self, stream=sys.stdout):
        logging.StreamHandler.__init__(self, stream)

    def format(self, record):
        text = logging.StreamHandler.format(self, record)
        color = self._get_color(record.levelno)
        return color + text + self.DEFAULT


handler = ColorStreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

''' Bugsnag config '''
if env != 'dev':
    bugsnag.configure(api_key=os.getenv('BUGSNAG_KEY'))
    bugsnag_handler = BugsnagHandler()
    # Error types of logs are output to Bugsnag.
    bugsnag_handler.setLevel(logging.ERROR)
    logger.addHandler(bugsnag_handler)


def log_function(function):
    ''' Main logging decorator '''

    def wrapper(*args, **kwargs):
        function_name = function.__name__
        logger.info('Executing "{0}"'.format(function_name))
        result = None
        try:
            result = function(*args, **kwargs)
        except Exception as e:
            logger.exception(
                f'Exception {e} with function "{function_name}"'
            )
            pass
        else:
            logger.info(f'"{function_name}" succesfully executed!')
        return result
    return wrapper
