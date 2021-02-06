import logging
from OpenAnalytics.LoggerOA.AppLoggersOA import main_logger
from OpenAnalytics.LoggerOA import DEBUG_LEVEL_DICT
from OpenAnalytics.ENV import GOOGLE_API_LOG_LEVEL, ENV_DEBUG_LEVEL_PATH
from dotenv import load_dotenv
from os import getenv

google_api_log = logging.getLogger("OA.google")

# Get Debug level
debug_level = logging.DEBUG
if ENV_DEBUG_LEVEL_PATH.exists():
    load_dotenv(ENV_DEBUG_LEVEL_PATH)
    debug_level = DEBUG_LEVEL_DICT[getenv(GOOGLE_API_LOG_LEVEL).lower()]
google_api_log.setLevel(debug_level)

# Define internal Global Variables
GOOGLE_AUTH_SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/contacts']
TOKEN_CRED_PICKLE = 'token_cred.pickle'


# Define Calendar Variables
CALENDAR_SERVICE = 'calendar'
CALENDAR_SERVICE_VERSION = 'v3'

# Define Contacts Group
PEOPLE_SERVICE = 'people'
PEOPLE_SERVICE_VERSION = 'v1'