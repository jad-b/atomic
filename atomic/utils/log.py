import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s [%(module)s]: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "atomic": {
            "handlers": ["console"],
            "propagate": False,
            "level": "DEBUG"
        }
    }
}

logging.config.dictConfig(LOGGING)


def get_logger(name):
    """Returns a child logger of "atomic", suffixed by ``name``.

    Forces the above configuration to be loaded.

    Args:
        name (str): Name of the child logger. Will be prefixed by "atomic.".

    Returns:
        :class:`~.logging.Logger`: Python logger.
    """
    return logging.getLogger("atomic." + name)
