# logger Directories

import logging

# create log for all applications
main_logger = logging.getLogger("OpenAnalytics")
main_logger.setLevel(logging.DEBUG)

calendar_logger = logging.getLogger("OpenAnalytics.Calendar")
auth_logger = logging.getLogger("OpenAnalytics.Auth")

# DEFINE HANDLERS FOR LOGGERS

# stream logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# DEFINE FORMARTER

# main formatter
date_format = "%H:%M:%S"
format_str = "%(asctime)s [%(levelname)s] %(name)-9s: %(message)s"
formatter = logging.Formatter(format_str, date_format)

# add formatters
stream_handler.setFormatter(formatter)

# add hanbdler to log
main_logger.addHandler(stream_handler)
