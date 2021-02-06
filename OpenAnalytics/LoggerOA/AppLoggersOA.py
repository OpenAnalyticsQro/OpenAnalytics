import logging
from OpenAnalytics.LoggerOA import OpenAnalyticsLoggerFormatter

# create log for all applications
main_logger = logging.getLogger("OA")
main_logger.setLevel(logging.DEBUG)


# DEFINE HANDLERS FOR LOGGERS

# stream logger
stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.DEBUG)

# add formatters
stream_handler.setFormatter(OpenAnalyticsLoggerFormatter())

# add hanbdler to log
main_logger.addHandler(stream_handler)