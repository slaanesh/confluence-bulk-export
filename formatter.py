import logging

class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter that adds color to specific log levels
    and formats the log output.
    """
    # Define the log format
    FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    COLOR_CODES = {
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow (change to red if desired)
        'ERROR': '\033[91m',  # Red
        'DEBUG': '\033[94m',  # Blue
        'CRITICAL': '\033[95m',  # Magenta
        'RESET': '\033[0m'  # Reset to default color
    }

    def __init__(self):
        super().__init__(fmt=self.FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record: logging.LogRecord) -> str:
        # Use the log level to determine the color
        log_color = self.COLOR_CODES.get(record.levelname, self.COLOR_CODES['RESET'])
        # Apply color to the log level name and format the message
        record.levelname = f"{log_color}{record.levelname}{self.COLOR_CODES['RESET']}"
        # Return the formatted log message
        return super().format(record)
