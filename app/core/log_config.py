logging_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "access": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr"
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": [
                "default"
            ],
            "propagate": "no"
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": [
                "access"
            ],
            "propagate": "no"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "default"
        ],
        "propagate": "no"
    }
}

if __name__ == "__main__":
    import logging.config

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
