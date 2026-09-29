import logging
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path


def create_logger(root):
    logger = logging.Logger('ala.' + str(id(root)))
    handler = RotatingFileHandler(Path(root)/'diagnostics.log', maxBytes=1_000_000,
                                  backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def safe_trace(error):
    # Exception strings may contain source text, credentials or user paths.
    return ' > '.join(f'{Path(f.filename).name}:{f.lineno}:{f.name}'
                      for f in traceback.extract_tb(error.__traceback__))
