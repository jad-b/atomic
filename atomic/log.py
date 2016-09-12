import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s [%(name)s] %(module)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'atomic': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'valence': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'cli': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG'
        },
        'api': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG'
        },
    }
}

logging.config.dictConfig(LOGGING)


def get_logger(name):
    """Returns a logger by the given name.

    Forces the above configuration to be loaded.
    """
    return logging.getLogger(name)
