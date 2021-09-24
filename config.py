import os

# Settings file

DB_CONNECTION = {
    'HOST': '127.0.0.1',
    'PORT': 5432,
    'USER': '',
    'PASSWORD': '',
    'DATABASE': 'mailkeeper',
}


INBOUND_URL = 'http://127.0.0.1:8000/accounts/post/'
BOUNCED_URL = 'http://127.0.0.1:8000/accounts/bounces/'

WEBHOOK_INBOUND_KEY = b'XXXXXXXXXXXXXXXXXXXXX'
WEBHOOK_BOUNCES_KEY = b'YYYYYYYYYYYYYYYYYYYYY'


BOUNCED_EMAIL_DOMAIN = 'bounce.example.com'
INBOUND_EMAIL_DOMAIN = 'reply.example.com'
X_MAILKEEPER_HEADER = 'X-MAILKEEPER-SIGNATURE'
IGNORE_EMAIL_LIST = ()

DEBUG = True

# Rabbitmq-server
RABBITMQ_HOST = '127.0.0.1'
QUEUE_NAME = 'inbound'

LOCAL_SETTINGS = os.environ.get(
    'LOCAL_SETTINGS', 'local_mailkeeper_config.py')

EVENTS_URLS = {
    'inbound': INBOUND_URL,
    'bounced': BOUNCED_URL,
}

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(message)s'
         },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'log_main': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': '/tmp/mailkeeper.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'log_main'],
            'level': 'ERROR',
        }
    }
}

if os.path.exists(LOCAL_SETTINGS):
    with open(LOCAL_SETTINGS) as local_config:
        exec(local_config.read())

if EVENTS_URLS:
    EVENTS_URLS = {
        'inbound': INBOUND_URL,
        'bounced': BOUNCED_URL,
    }

WEBHOOK_KEYS = {
    'inbound': WEBHOOK_INBOUND_KEY,
    'bounced': WEBHOOK_BOUNCES_KEY,
}

DB_URL_TEMPLATE = '{DRIVER}://{USER}:{PASSWORD}@{HOST}/{DATABASE}'
A_DB_URL = DB_URL_TEMPLATE.format(DRIVER='postgresql+asyncpg', **DB_CONNECTION)
