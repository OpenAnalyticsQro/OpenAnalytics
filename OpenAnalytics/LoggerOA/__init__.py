import logging


# Define Macros ref- https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
GREY_LOG_COLOR = "\x1b[38;5;153m"
YELLOW_LOG_COLOR = "\x1b[38;5;226m"
RED_LOG_COLOR = "\x1b[38;5;204m"
CRITICAL_LOG_COLOR = "\x1b[38;5;208m"
RESET_LOG_COLOR = "\x1b[0m"
BLUE_LOG_COLOR = "\x1b[38;5;66m"
GREEN_LOG_COLOR = "\x1b[38;5;118m"

MAIN_LOG_FORMAT_STR = "{}%(asctime)s{} {}[%(levelname)s]{} %(name)s: %(message)s"

DEBUG_LEVEL_FORMATS = {
    logging.DEBUG: MAIN_LOG_FORMAT_STR.format(
        BLUE_LOG_COLOR, RESET_LOG_COLOR, GREY_LOG_COLOR, RESET_LOG_COLOR
    ),
    logging.INFO: MAIN_LOG_FORMAT_STR.format(
        BLUE_LOG_COLOR, RESET_LOG_COLOR, GREEN_LOG_COLOR, RESET_LOG_COLOR
    ),
    logging.WARNING: MAIN_LOG_FORMAT_STR.format(
        BLUE_LOG_COLOR, RESET_LOG_COLOR, YELLOW_LOG_COLOR, RESET_LOG_COLOR
    ),
    logging.ERROR: MAIN_LOG_FORMAT_STR.format(
        BLUE_LOG_COLOR, RESET_LOG_COLOR, RED_LOG_COLOR, RESET_LOG_COLOR
    ),
    logging.CRITICAL: MAIN_LOG_FORMAT_STR.format(
        BLUE_LOG_COLOR, RESET_LOG_COLOR, CRITICAL_LOG_COLOR, RESET_LOG_COLOR
    ),
}

DEBUG_LEVEL_DICT = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class OpenAnalyticsLoggerFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    def format(self, record):
        log_fmt = DEBUG_LEVEL_FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
