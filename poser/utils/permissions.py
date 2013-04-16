# -*- coding: utf-8 -*-
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

# thread local support
_thread_locals = local()


def set_current_user(user):
    """
    Assigns current user from request to thread_locals, used by
    CurrentUserMiddleware.
    """
    _thread_locals.user = user


def get_current_user():
    """
    Returns current user, or None
    """
    return getattr(_thread_locals, 'user', None)


def has_generic_permission(page_id, user, attr):
    """
    Permission getter for single page with given id.
    """
    return user.has_perm(attr, page_id)
