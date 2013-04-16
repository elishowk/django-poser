# -*- coding: utf-8 -*-
import os

gettext = lambda s: s


urlpatterns = []


def configure(**extra):
    from django.conf import settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'poser.test_utils.cli'
    defaults = dict(
        CACHE_BACKEND = 'locmem:///',
        DEBUG = True,
        TEMPLATE_DEBUG = True,
        DATABASE_SUPPORTS_TRANSACTIONS = True,
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        SITE_ID = 1,
        USE_I18N = True,
        MEDIA_ROOT = '/media/',
        STATIC_ROOT = '/static/',
        POSER_MEDIA_ROOT = '/poser-media/',
        POSER_MEDIA_URL = '/poser-media/',
        MEDIA_URL = '/media/',
        STATIC_URL = '/static/',
        ADMIN_MEDIA_PREFIX = '/static/admin/',
        EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend',
        SECRET_KEY = 'key',
        TEMPLATE_LOADERS = (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            'django.template.loaders.eggs.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS = [
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.i18n",
            "django.core.context_processors.debug",
            "django.core.context_processors.request",
            "django.core.context_processors.media",
            'django.core.context_processors.csrf',
            "poser.context_processors.media",
            "django.core.context_processors.static",
        ],
        TEMPLATE_DIRS = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'project', 'templates'))
        ],
        MIDDLEWARE_CLASSES = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.doc.XViewMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'poser.middleware.user.CurrentUserMiddleware',
            'poser.middleware.page.CurrentPageMiddleware',
        ],
        INSTALLED_APPS = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            'tastypie',
            'guardian',
            'poser',
            'poser.test_utils.project.sampleapp',
            'south',
        ],
        POSER_PERMISSION = True,
        POSER_APPHOOKS=[],
        POSER_REDIRECTS = True,
        POSER_PLUGIN_PROCESSORS = tuple(),
        POSER_PLUGIN_CONTEXT_PROCESSORS = tuple(),
        SOUTH_TESTS_MIGRATE = False,
        TEST_RUNNER = 'poser.test_utils.runners.NormalTestRunner',
        JUNIT_OUTPUT_DIR = '.',
        TIME_TESTS = False,
        ROOT_URLCONF = 'poser.test_utils.cli',
        PASSWORD_HASHERS = (
            'django.contrib.auth.hashers.MD5PasswordHasher',
        )
    )
    defaults.update(extra)
    settings.configure(**defaults)
    from poser.conf import patch_settings
    patch_settings()
    from south.management.commands import patch_for_test_db_setup
    patch_for_test_db_setup()
    from django.contrib import admin
    admin.autodiscover()
