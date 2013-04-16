# -*- coding: utf-8 -*-
from poser.apphook_pool import apphook_pool
from poser.views import details
from django.conf import settings
from django.conf.urls.defaults import url, patterns

if settings.APPEND_SLASH:
    reg = url(r'^(?P<slug>[0-9A-Za-z-_.//]+)/$', details, name='pages-details-by-slug')
else:
    reg = url(r'^(?P<slug>[0-9A-Za-z-_.//]+)$', details, name='pages-details-by-slug')

urlpatterns = [
    # Public pages
    url(r'^$', details, {'slug':''}, name='pages-root'),
    reg,
]

if apphook_pool.get_apphooks():
    """If there are some application urls, add special resolver, so we will
    have standard reverse support.
    """
    from poser.appresolver import get_app_patterns
    urlpatterns = get_app_patterns() + urlpatterns
    
urlpatterns = patterns('', *urlpatterns)
