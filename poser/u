# -*- coding: utf-8 -*-
from poser.apphook_pool import apphook_pool
from poser.appresolver import get_app_urls
from poser.utils.page_resolver import get_page_from_request
from django.conf.urls.defaults import patterns
from django.core.urlresolvers import resolve, Resolver404
from django.http import Http404, HttpResponseRedirect


def _handle_no_page(request, slug):
    raise Http404('poser did not found "%s"' % slug)


def details(request, slug):
    """
    Takes a request and a slug, renders the page's template.
    """
    # Get a Page model object from the request
    page = get_page_from_request(request, use_path=slug)
    if not page:
        return _handle_no_page(request, slug)

    # Check if the page has a redirect url defined
    redirect_url = page.get_redirect()
    if redirect_url:
        # prevent redirect to self
        own_urls = [
            'http%s://%s%s' % ('s' if request.is_secure() else '', request.get_host(), request.path),
            '/%s' % (request.path),
            request.path,
        ]
        if redirect_url not in own_urls:
            return HttpResponseRedirect(redirect_url)

    if not page.has_view_permission(request):
        return _handle_no_page(request, slug)

    if apphook_pool.get_apphooks():
        # There are apphooks in the pool. Let's see if there is one for the
        # current page
        # since we always have a page at this point, applications_page_check() is
        # pointless
        app_name = page.get_application()
        if app_name:
            app = apphook_pool.get_apphook(app_name)
            pattern_list = []
            for urlpatterns in get_app_urls(app.urls):
                pattern_list += urlpatterns
            urlpatterns = patterns('', *pattern_list)
            try:
                view, args, kwargs = resolve('/', tuple(urlpatterns))
                return view(request, *args, **kwargs)
            except Resolver404:
                pass
        else:
            return _handle_no_page(request, slug)
