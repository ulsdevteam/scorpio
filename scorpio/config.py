DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'scorpio-db',
        'PORT': 5432,
    }
}

ELASTICSEARCH = {
    'default': {
        'hosts': ['elasticsearch:9200']
    },
}

STATIC_URL = '/indexer/static/'

ALLOWED_HOSTS = ['localhost', 'scorpio-web']
