# -*- coding: utf-8 -*-
from poser.apphook_pool import apphook_pool
from poser.utils.page_resolver import get_page_queryset

from django.conf import settings
from django.conf.urls.defaults import patterns
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import RegexURLResolver, Resolver404, reverse, \
    RegexURLPattern
from django.utils.importlib import import_module

APP_RESOLVERS = []


def clear_app_resolvers():
    global APP_RESOLVERS
    APP_RESOLVERS = []


def applications_page_check(request, current_page=None, path=None):
    """Tries to find if given path was resolved over application.
    Applications have higher priority than other poser pages.
    """
    if current_page:
        return current_page
    if path is None:
        # We should get in this branch only if an apphook is active on /
        # This removes the non-POSER part of the URL.
        path = request.path.replace(reverse('pages-root'), '', 1)
    # check if application resolver can resolve this
    for resolver in APP_RESOLVERS:
        try:
            page_id = resolver.resolve_page_id(path)
            # yes, it is application page
            page = get_page_queryset(request).get(id=page_id)
            # If current page was matched, then we have some override for content
            # from poser, but keep current page. Otherwise return page to which was application assigned.
            return page
        except Resolver404:
            # Raised if the page is not managed by an apphook
            pass
    return None


class AppRegexURLResolver(RegexURLResolver):
    page_id = None
    url_patterns = None

    def resolve_page_id(self, path):
        """Resolves requested path similar way how resolve does, but instead
        of return callback,.. returns page_id to which was application
        assigned.
        """
        tried = []
        match = self.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in self.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404, e:
                    if 'tried' in e.args[0]:
                        tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
                    elif 'path' in e.args[0]:
                        tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['path']])
                else:
                    if sub_match:
                        return pattern.page_id
                    tried.append(pattern.regex.pattern)
            raise Resolver404, {'tried': tried, 'path': new_path}


def recurse_patterns(path, pattern_list, page_id):
    """
    Recurse over a list of to-be-hooked patterns for a given path prefix
    """
    newpatterns = []
    for pattern in pattern_list:
        app_pat = pattern.regex.pattern
        # make sure we don't get patterns that start with more than one '^'!
        if not app_pat.endswith('$'):
            return newpatterns
        app_pat = app_pat.lstrip('^')
        path = path.lstrip('^')
        regex = r'^%s%s' % (path, app_pat)
        if isinstance(pattern, RegexURLResolver):
            # this is an 'include', recurse!
            resolver = RegexURLResolver(regex, 'poser_appresolver',
                                        pattern.default_kwargs,
                                        pattern.app_name,
                                        pattern.namespace)
            resolver.page_id = page_id
            # see lines 243 and 236 of urlresolvers.py to understand the next line
            resolver._urlconf_module = recurse_patterns(regex, pattern.url_patterns, page_id)
        else:
            # Re-do the RegexURLPattern with the new regular expression
            resolver = RegexURLPattern(regex, pattern.callback,
                                       pattern.default_args, pattern.name)
            resolver.page_id = page_id
        newpatterns.append(resolver)
    return newpatterns


def _flatten_patterns(patternstoflatten):
    flat = []
    for pattern in patternstoflatten:
        if isinstance(pattern, RegexURLResolver):
            flat += _flatten_patterns(pattern.url_patterns)
        else:
            flat.append(pattern)
    return flat


def get_app_urls(urls):
    for urlconf in urls:
        if isinstance(urlconf, basestring):
            mod = import_module(urlconf)
            if not hasattr(mod, 'urlpatterns'):
                raise ImproperlyConfigured(
                    "URLConf `%s` has no urlpatterns attribute" % urlconf)
            yield getattr(mod, 'urlpatterns')
        else:
            yield urlconf


def get_patterns_for_page(path, page):
    """
    Resolve the urlconf module for a path+title combination
    Returns a list of url objects.
    """
    app = apphook_pool.get_apphook(page.application)
    patterns_page = []
    for pattern_list in get_app_urls(app.urls):
        if path and not path.endswith('/'):
            path += '/'
        page_id = page.id
        patterns_page += recurse_patterns(path, pattern_list, page_id)
    patterns_page = _flatten_patterns(patterns_page)
    return patterns_page


def get_app_patterns():
    """
    Get a list of patterns for all hooked apps at start-up time.

    How this works:

    By looking through all pages with an app hook (application_urls) we find all
    urlconf modules we have to hook into.

    All 'normal' patterns from the urlconf get re-written by prefixing them with
    the title path and then included into the poser url patterns.
    """
    from poser.models import Page
    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        current_site = None
    included = []

    page_qs = Page.objects.filter(site=current_site)

    use_namespaces = False
    hooked_applications = []

    # Loop over all titles with an application hooked to them
    for page in page_qs.exclude(application=None).exclude(application='').select_related():
        path = page.path
        if use_namespaces:
            mixid = "%s:%s:%s" % (path + "/", page.application)
        else:
            mixid = "%s:%s" % (path + "/", page.application)
        if mixid in included:
            # don't add the same thing twice
            continue
        if not settings.APPEND_SLASH:
            path += '/'
        hooked_applications += get_patterns_for_page(path, page)
        included.append(mixid)
    # Build the app patterns to be included in the poser urlconfs
    app_patterns = []
    if use_namespaces:
        for ns, currentpatterns in hooked_applications.items():
            extra_patterns = patterns('', *currentpatterns)
            resolver = AppRegexURLResolver(r'', 'app_resolver', namespace=ns)
            resolver.url_patterns = extra_patterns
            app_patterns.append(resolver)
            APP_RESOLVERS.append(resolver)
    else:
        extra_patterns = patterns('', *hooked_applications)
        resolver = AppRegexURLResolver(r'', 'app_resolver')
        resolver.url_patterns = extra_patterns
        app_patterns.append(resolver)
        APP_RESOLVERS.append(resolver)
    return app_patterns
