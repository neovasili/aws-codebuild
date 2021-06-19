import logging

HEADER_LVL_NUM = 100
logging.addLevelName(HEADER_LVL_NUM, "HEADER")


def header(self, message, *args, **kws):
    self._log(HEADER_LVL_NUM, message, args, **kws)


logging.Logger.header = header


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors."""

    green = "\x1b[32m"
    blue = "\x1b[1;34m"
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)-15s] %(levelname)s - %(message)s"
    simplified_format = "[%(asctime)-15s] %(message)s"

    FORMATS = {
        logging.DEBUG: blue + format + reset,  # Num: 10
        logging.INFO: grey + format + reset,  # Num: 20
        logging.WARNING: yellow + format + reset,  # Num: 30
        logging.ERROR: red + format + reset,  # Num: 40
        logging.CRITICAL: bold_red + format + reset,  # Num: 50
        HEADER_LVL_NUM: green + simplified_format + reset,
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format)

        return formatter.format(record)
