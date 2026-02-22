LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'expenses': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'purchases': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'documents': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
