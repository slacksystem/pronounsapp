import logging
import logging.config

# Define the configuration dictionary
LOGGING_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}


def configure_logging(logfilename: str, loglevel: str = "DEBUG") -> None:
    """Configure the logging system.

    Args:
        logfilename (str): The name of the log file.
        loglevel (str, optional): The log level. Defaults to "DEBUG".
    Returns:
        None
    """

    # Add the log file name
    LOGGING_CONF["handlers"]["file"]["filename"] = logfilename
    # Add the log level
    LOGGING_CONF["handlers"]["console"]["level"] = loglevel
    LOGGING_CONF["handlers"]["file"]["level"] = loglevel

    # load the configuration
    logging.config.dictConfig(LOGGING_CONF)
