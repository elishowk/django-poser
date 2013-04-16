from __future__ import with_statement
from poser.api import create_page
from poser.apphook_pool import apphook_pool
from poser.test_utils.testcases import SettingsOverrideTestCase
from poser.test_utils.util.context_managers import SettingsOverride
from poser.views import _handle_no_page, details
from django.conf import settings
from django.core.urlresolvers import clear_url_caches
from django.http import Http404, HttpResponse
import sys


APP_NAME = 'SampleApp'
APP_MODULE = "poser.test_utils.project.sampleapp.poser_app"


class ViewTests(SettingsOverrideTestCase):
    urls = 'poser.test_utils.project.urls_for_apphook_tests'
    settings_overrides = {}
    
    def setUp(self):
        clear_url_caches()
    
    def test_handle_no_page(self):
        """
        Test handle nopage correctly works with DEBUG=True
        """
        request = self.get_request('/')
        slug = '/'
        self.assertRaises(Http404, _handle_no_page, request, slug)
        with SettingsOverride(DEBUG=True):
            request = self.get_request('/')
            slug = '/'
            self.assertRaises(Http404, _handle_no_page, request, slug)
            
    def test_apphook_not_hooked(self):
        """
        Test details view when apphook pool has apphooks, but they're not
        actually hooked
        """
        if APP_MODULE in sys.modules:
            del sys.modules[APP_MODULE]
        apphooks = (
            '%s.%s' % (APP_MODULE, APP_NAME),
        )
        create_page("page2", "nav_playground.html", published=True)
        with SettingsOverride(POSER_APPHOOKS=apphooks):
            apphook_pool.clear()
            response = self.client.get('/')
            self.assertEqual(response.status_code, 404)
            apphook_pool.clear()
    
    def test_external_redirect(self):
        # test external redirect
        redirect_one = 'https://www.django-poser.org/'
        one = create_page("one", "nav_playground.html", published=True,
                          redirect=redirect_one)
        url = one.get_absolute_url()
        request = self.get_request(url)
        response = details(request, url.strip('/'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], redirect_one)
        
    def test_internal_forced_redirect(self):
        redirect_one = 'https://www.django-poser.org/'
        redirect_three = '/'
        one = create_page("one", "nav_playground.html", published=True,
                          redirect=redirect_one)
        three = create_page("three", "nav_playground.html",
                            published=True, redirect=redirect_three)
        url = three.get_absolute_url()
        request = self.get_request(url)
        response = details(request, url.strip('/'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], redirect_three)
        
    def test_redirect_to_self(self):
        one = create_page("one", "nav_playground.html", published=True,
                          redirect='/')
        url = one.get_absolute_url()
        request = self.get_request(url)
        response = details(request, url.strip('/'))
        self.assertEqual(response.status_code, 302)
        
    def test_redirect_to_self_with_host(self):
        one = create_page("one", "nav_playground.html", published=True,
                          redirect='http://testserver/')
        url = one.get_absolute_url()
        request = self.get_request(url)
        response = details(request, url.strip('/'))
        self.assertEqual(response.status_code, 302)
    
    def test_login_required(self):
        create_page("page", "nav_playground.html", published=True,
                         login_required=True)
        request = self.get_request('/page/')
        response = details(request, '')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '%s?next=/page/' % settings.LOGIN_URL)

