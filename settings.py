MIDDLEWARE = [
    # ... other middleware
    'authentication.middleware.ProfileAuthenticationMiddleware',
]

# Set DEBUG to True for development
DEBUG = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'registration' / 'templates',
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'authentication.context_processors.profile_context',
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'expenses' / 'static',
    BASE_DIR / 'purchases' / 'static',
    BASE_DIR / 'banking' / 'static',
    BASE_DIR / 'banking' / 'static' / 'banking',
    BASE_DIR / 'reports' / 'static',
    BASE_DIR / 'registration' / 'static',
    BASE_DIR / 'access_control' / 'static',
    BASE_DIR / 'people' / 'static',
    BASE_DIR / 'project_management' / 'static',
    BASE_DIR / 'site_admin' / 'static',
]

# The absolute path to the directory where collectstatic will collect static files for deployment
STATIC_ROOT = BASE_DIR / 'staticfiles'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'clients.apps.ClientsConfig',
    'sales',
    'documents',
    'dashboard',
    'django_extensions',
    'authentication',
    'expenses.apps.ExpensesConfig',
    'purchases.apps.PurchasesConfig',
    'banking.apps.BankingConfig',
    'reports.apps.ReportsConfig',
    'access_control.apps.AccessControlConfig',
    'registration.apps.RegistrationConfig',
    'people.apps.PeopleConfig',
    'project_management.apps.ProjectManagementConfig',
    'site_admin.apps.SiteAdminConfig',
]

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'project_management.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'project_management': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}