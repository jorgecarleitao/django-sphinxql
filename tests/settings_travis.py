import os

if os.environ['BACKEND'] == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'sphinx_example',
            'TEST_NAME': 'sphinx_example_test',
            'USER': 'root',
            },
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'sphinx_example',
            'TEST_NAME': 'sphinx_example_test',
            'USER': 'postgres'
            },
        }

INSTALLED_APPS = ('sphinxql', 'tests.query', 'tests.queryset',
                  'tests.indexing', 'tests.foreign_relationships')

SECRET_KEY = "django_tests_secret_key"

MIDDLEWARE_CLASSES = ()

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# we add 'U+00E2' to test unicode
# we cannot override settings since this is used at config time.
INDEXES = {
    'path': os.path.join(BASE_DIR, '_index'),
    'sphinx_path': BASE_DIR,
    'index_params': {'charset_table': '0..9, A..Z->a..z, _, a..z, /, '
                                      'U+00E2'},
    'searchd_params': {'binlog_path': ''}
}
