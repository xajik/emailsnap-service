import logging


appLogger = logging.getLogger("EmailSnap")
appLogger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.ERROR)
