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
        'hosts': ['elasticsearch:9200'],
        'index': 'default'
    },
}

STATIC_URL = '/indexer/static/'

ALLOWED_HOSTS = ['localhost', 'scorpio-web']

SILKY_PYTHON_PROFILER = True

SCHEMA_URL = 'https://raw.githubusercontent.com/RockefellerArchiveCenter/rac-data-model/master/schema.json'
SCHEMA_PATH = 'schema.json'
