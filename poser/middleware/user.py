# -*- coding: utf-8 -*-
"""This is ugly, but seems there's no other way how to do what we need for
permission system.

This middleware is required only when POSER_PERMISSION = True.
"""

class CurrentUserMiddleware(object):
    def process_request(self, request):
        from poser.utils.permissions import set_current_user
        set_current_user(getattr(request, 'user', None))
