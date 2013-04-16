# -*- coding: utf-8 -*-
from django.conf import settings as d_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_resolver, get_script_prefix, \
    NoReverseMatch
from pagemodel import *
from django.utils.translation import get_language
import django.core.urlresolvers
# must be last
from poser import signals as s_import
from pagemeta import *


def validate_settings():
    if not "django.core.context_processors.request" in d_settings.TEMPLATE_CONTEXT_PROCESSORS:
        raise ImproperlyConfigured('django-poser needs django.core.context_processors.request in settings.TEMPLATE_CONTEXT_PROCESSORS to work correctly.')

validate_settings()
