import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mailkeeper',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'main': {
        'NAME': 'main',
        'ENGINE': 'django.db.backends.postgresql',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
DATABASE_ROUTERS = ['mailkeeper.models.AuthRouter']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'mailkeeper',
)

TEMPLATES = [
   {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            )
        }
   }
]

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'mailkeeper.urls'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
AUTH_USER_MODEL = 'mailkeeper.User'

LOCAL_SETTINGS = os.environ.get(
    'LOCAL_SETTINGS', 'mailkeeper_local_settings.py')

if os.path.exists(LOCAL_SETTINGS):
    with open(LOCAL_SETTINGS) as local_settings:
        exec(local_settings.read(), globals())
