# -*- coding: utf-8 -*-
from django.conf import settings

def media(request):
    """
    Adds media-related context variables to the context.
    """
    return {'POSER_MEDIA_URL': settings.POSER_MEDIA_URL}
