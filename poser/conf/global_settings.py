# -*- coding: utf-8 -*-
"""
Global poser settings, are applied if there isn't value defined in project
settings. All available settings are listed here. Please don't put any
functions / test inside, if you need to create some dynamic values / tests,
take look at poser.conf.patch
"""
import os
from django.conf import settings

# The id of default Site instance to be used for multisite purposes.
SITE_ID = 1

POSER_PERMISSION = True

# a tuple of python path to AppHook Classes. Overwrites the auto-discovered apphooks.
POSER_APPHOOKS = ('poser.test_utils.project.sampleapp.poser_app.SampleApp',)

# Path for POSER media (uses <MEDIA_ROOT>/poser by default)
POSER_MEDIA_PATH = 'poser/'
POSER_MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, POSER_MEDIA_PATH)
POSER_MEDIA_URL = os.path.join(settings.MEDIA_URL, POSER_MEDIA_PATH)

# Cache prefix so one can deploy several sites on one cache server
#POSER_CACHE_PREFIX = "%s" % settings.SITE_ID + '-poser-'

ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
)

SOUTH_TESTS_MIGRATE = False

# minimal
INSTALLED_APPS = (
    'poser.test_utils.project.sampleapp',
    'guardian',
)

POSER_PUBLIC_FOR = 'all'
