# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def post_patch_check():
    """Post patch check, just make sure there isn't any misconfiguration. All
    the code for checking settings should go here.
    """
    # check if is user middleware installed
    if settings.POSER_PERMISSION and not 'poser.middleware.user.CurrentUserMiddleware' in settings.MIDDLEWARE_CLASSES:
        raise ImproperlyConfigured('POSER Permission system requires poser.middleware.user.CurrentUserMiddleware.\n'
            'Please put it into your MIDDLEWARE_CLASSES in settings file')
