import logging
from OpenAnalytics.LoggerOA.AppLoggersOA import main_logger
from OpenAnalytics.ENV import AIR_TABLE_LOG_LEVEL, ENV_DEBUG_LEVEL_PATH
from OpenAnalytics.LoggerOA import DEBUG_LEVEL_DICT
from dotenv import load_dotenv
from os import getenv

air_table_log = logging.getLogger("OA.airTable")

# Get Debug level
debug_level = logging.DEBUG
if ENV_DEBUG_LEVEL_PATH.exists():
    load_dotenv(ENV_DEBUG_LEVEL_PATH)
    debug_level = DEBUG_LEVEL_DICT[getenv(AIR_TABLE_LOG_LEVEL).lower()]
    print(f"level {debug_level}: {getenv(AIR_TABLE_LOG_LEVEL).lower()} {logging.DEBUG} {logging.INFO}")
air_table_log.setLevel(debug_level)