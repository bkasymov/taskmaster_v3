import logging
import os

LOGLEVELCONSTANT = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)
SERVER_PORT = '8081'
STATUS = {
    'NOT_STARTED': -1,
    'FINISHED': -2,
    'STOPPED': -3,
}