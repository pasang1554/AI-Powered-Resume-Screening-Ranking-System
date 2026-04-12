import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    # File handler for persistence
    fileHandler = logging.FileHandler('backend.log')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger

# Initialize logger
api_logger = setup_logging()
