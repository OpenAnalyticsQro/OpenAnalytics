# logger Directories

import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    blue = "\x1b[0;34m"
    green = "\x1b[0;32m"
    format_str = "{}%(asctime)s{} {}[%(levelname)s]{} %(name)-9s: %(message)s"

    FORMATS = {
        logging.DEBUG: format_str.format(blue, reset, grey, reset),
        logging.INFO: format_str.format(blue, reset, green, reset),
        logging.WARNING: format_str.format(blue, reset, yellow, reset),
        logging.ERROR: format_str.format(blue, reset, red, reset),
        logging.CRITICAL: format_str.format(blue, reset, bold_red, reset),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create log for all applications
main_logger = logging.getLogger("OpenAnalytics")
main_logger.setLevel(logging.DEBUG)

# Define app Loggers
calendar_logger = logging.getLogger("OpenAnalytics.Calendar")
auth_logger = logging.getLogger("OpenAnalytics.Auth")
flask_logger = logging.getLogger("OpenAnalytics.Flask")
contacts_logger = logging.getLogger("OpenAnalytics.Contacts")

# DEFINE HANDLERS FOR LOGGERS

# stream logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# DEFINE FORMARTER

# main formatter
date_format = "%H:%M:%S"
format_str = "%(asctime)s [%(levelname)s] %(name)-9s: %(message)s"
formatter = logging.Formatter(format_str, date_format)
formatter = CustomFormatter()

# add formatters
stream_handler.setFormatter(formatter)

# add hanbdler to log
main_logger.addHandler(stream_handler)
