from django.conf import settings
from tastypie.authentication import Authentication
from django.middleware.csrf import _sanitize_token, constant_time_compare


class SessionHeadersAuthentication(Authentication):
    """
    An authentication mechanism that piggy-backs on Django sessions & auth

    This is useful when the API is NOT talking to Javascript on the same domain,
    but it still relies on the user being logged in through the standard Django login

    on POST : requires a valid CSRF token sent in Header 'HTTP_X_CSRFTOKEN'


    """
    def is_authenticated(self, request, **kwargs):
        """
        Checks to make sure the user is logged in & has a Django session.
        """
        # Cargo-culted from Django 1.3/1.4's ``django/middleware/csrf.py``.
        # We can't just use what's there, since the return values will be
        # wrong.
        # We also can't risk accessing ``request.POST``, which will break with
        # the serialized bodies.
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return request.user.is_authenticated()

        if getattr(request, '_dont_enforce_csrf_checks', False):
            return request.user.is_authenticated()

        csrf_token = _sanitize_token(request.META.get(settings.CSRF_COOKIE_NAME, ''))

        request_csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        if not constant_time_compare(request_csrf_token, csrf_token):
            return False

        return request.user.is_authenticated()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """
        return request.user.username

