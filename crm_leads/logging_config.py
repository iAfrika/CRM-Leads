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
<<<<<<< HEAD
    },
    'loggers': {
        'expenses': {
            'handlers': ['console'],
=======
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'crm_leads.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'expenses': {
            'handlers': ['console', 'file'],
>>>>>>> d781b6071826b1e9eeb8bf33453b359a2cce4225
            'level': 'INFO',
            'propagate': True,
        },
        'purchases': {
<<<<<<< HEAD
            'handlers': ['console'],
=======
            'handlers': ['console', 'file'],
>>>>>>> d781b6071826b1e9eeb8bf33453b359a2cce4225
            'level': 'INFO',
            'propagate': True,
        },
        'documents': {
<<<<<<< HEAD
            'handlers': ['console'],
=======
            'handlers': ['console', 'file'],
>>>>>>> d781b6071826b1e9eeb8bf33453b359a2cce4225
            'level': 'INFO',
            'propagate': True,
        },
    },
}
