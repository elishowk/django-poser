# -*- coding: utf-8 -*-
from poser.apphook_pool import apphook_pool
from poser.views import details
from poser.rest import PageResource, SiteResource, UserResource
from tastypie.api import Api
from django.conf import settings
from django.conf.urls.defaults import url, patterns, include
from django.views.generic.simple import direct_to_template

poser_api = Api(api_name='poser_api')
poser_api.register(PageResource())
poser_api.register(SiteResource())
poser_api.register(UserResource())

if settings.APPEND_SLASH:
    reg = url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', details, name='pages-details-by-slug')
else:
    reg = url(r'^(?P<slug>[0-9A-Za-z-_.//]+)$', details, name='pages-details-by-slug')

urlpatterns = [
    url(r'^$', direct_to_template, {'template': 'poser/index.html'}, name='pages-root'),
    (r'', include(poser_api.urls)),
    reg,
]

if apphook_pool.get_apphooks():
    """
    If there is a root  application url, add special resolver
    under '^my-page-path/'
    """
    from poser.appresolver import get_app_patterns
    urlpatterns = get_app_patterns() + urlpatterns


urlpatterns = patterns('', *urlpatterns)
