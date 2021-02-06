import logging
from OpenAnalytics.LoggerOA import OpenAnalyticsLoggerFormatter, DEBUG_LEVEL_DICT
from OpenAnalytics.ENV import ENV_DEBUG_LEVEL_PATH, MAIN_DEBUG_LEVEL
from dotenv import load_dotenv
from os import getenv

# create log for all applications
main_logger = logging.getLogger("OA")

# Get Debug level
debug_level = logging.DEBUG
if ENV_DEBUG_LEVEL_PATH.exists():
    load_dotenv(ENV_DEBUG_LEVEL_PATH)
    main_logger.setLevel(DEBUG_LEVEL_DICT[getenv(MAIN_DEBUG_LEVEL).lower()])



# DEFINE HANDLERS FOR LOGGERS

# stream logger
stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.DEBUG)

# add formatters
stream_handler.setFormatter(OpenAnalyticsLoggerFormatter())

# add hanbdler to log
main_logger.addHandler(stream_handler)