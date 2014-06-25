
# for testing postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sphinx_example',
        'TEST_NAME': 'sphinx_example_test',
        'USER': 'sphinx_example',
        'PASSWORD': 'test'
    },
}

# for testing mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sphinx_example',
        'TEST_NAME': 'sphinx_example_test',
        'USER': 'sphinx_example',
    },
}

INSTALLED_APPS = ('tests.query', 'tests.queryset', 'tests.indexing')

SECRET_KEY = "django_tests_secret_key"

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INDEXES = {
    'PATH': os.path.join(BASE_DIR, '_index'),
    'sphinx_path': BASE_DIR,
}
