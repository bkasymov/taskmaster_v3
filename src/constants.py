import logging
import os

LOGLEVELCONSTANT = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)
