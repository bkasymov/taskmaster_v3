import logging
import os

LOGLEVELCONSTANT = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)

STATUS = {
    'NOT_STARTED': -1,
    'STOPPED': -3,
    'FINISHED': -2,
}