# -*- coding: utf-8 -*-
from __future__ import with_statement
from poser.api import create_page
from poser.apphook_pool import apphook_pool
from poser.appresolver import (applications_page_check, clear_app_resolvers, 
    get_app_patterns)
from poser.test_utils.testcases import POSERTestCase
from poser.test_utils.util.context_managers import SettingsOverride
from django.contrib.auth.models import User
from django.core.urlresolvers import clear_url_caches, reverse
import sys



APP_NAME = 'SampleApp'
APP_MODULE = "poser.test_utils.project.sampleapp.poser_app"


class ApphooksTestCase(POSERTestCase):

    def setUp(self):
        clear_app_resolvers()
        clear_url_caches()
        
        if APP_MODULE in sys.modules:
            del sys.modules[APP_MODULE]

    def tearDown(self):
        clear_app_resolvers()
        clear_url_caches()

        if APP_MODULE in sys.modules:
            del sys.modules[APP_MODULE]
    
    def test_explicit_apphooks(self):
        """
        Test explicit apphook loading with the POSER_APPHOOKS setting.
        """
        apphooks = (
            '%s.%s' % (APP_MODULE, APP_NAME),
        )
        with SettingsOverride(POSER_APPHOOKS=apphooks):
            apphook_pool.clear()
            hooks = apphook_pool.get_apphooks()
            app_names = [hook[0] for hook in hooks]
            self.assertEqual(len(hooks), 1)
            self.assertEqual(app_names, [APP_NAME])
            apphook_pool.clear()
            
    def test_implicit_apphooks(self):
        """
        Test implicit apphook loading with INSTALLED_APPS + poser_app.py
        """
            
        apps = ['poser.test_utils.project.sampleapp']
        with SettingsOverride(INSTALLED_APPS=apps, ROOT_URLCONF='poser.test_utils.project.urls_for_apphook_tests'):
            apphook_pool.clear()
            hooks = apphook_pool.get_apphooks()
            app_names = [hook[0] for hook in hooks]
            self.assertEqual(len(hooks), 1)
            self.assertEqual(app_names, [APP_NAME])
            apphook_pool.clear()
    
    def test_apphook_on_root(self):
        
        with SettingsOverride(ROOT_URLCONF='poser.test_utils.project.urls_for_apphook_tests'):
            apphook_pool.clear()    
            superuser = User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            page = create_page("apphooked-page", "nav_playground.html",
                               created_by=superuser, published=True, apphook="SampleApp")
            blank_page = create_page("not-apphooked-page", "nav_playground.html",
                                     created_by=superuser, published=True, apphook="", slug='blankapp')
            self.assertTrue(page.publish())
            self.assertTrue(blank_page.publish())
    
            response = self.client.get("/apphooked-page/")
            self.assertTemplateUsed(response, 'sampleapp/home.html')

            response = self.client.get('/blankapp/')
            self.assertTemplateUsed(response, 'nav_playground.html')

            apphook_pool.clear()

    def test_apphook_on_root_reverse(self):
        with SettingsOverride(ROOT_URLCONF='poser.test_utils.project.urls_for_apphook_tests'):
            apphook_pool.clear()
            superuser = User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            page = create_page("apphooked-page", "nav_playground.html",
                created_by=superuser, published=True, apphook="SampleApp")
            self.assertTrue(page.publish())

            self.assertFalse(reverse('sample-settings').startswith('//'))

            apphook_pool.clear()
    
    def test_get_page_for_apphook(self):
            
        with SettingsOverride(ROOT_URLCONF='poser.test_utils.project.second_urls_for_apphook_tests'):
    
            apphook_pool.clear()    
            superuser = User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            child_child_page = create_page("child_child_page", "nav_playground.html",
                created_by=superuser, published=True, apphook='SampleApp')
            
            child_child_page.publish()
            # publisher_public is set to draft on publish, issue with onetoone reverse
            child_child_page = self.reload(child_child_page) 
            
            en_title = child_child_page.get_title()

            path = reverse('sample-settings')
            
            response = self.client.get(path)
            self.assertEquals(response.status_code, 200)

            self.assertTemplateUsed(response, 'sampleapp/home.html')
            self.assertContains(response, en_title)
            
            apphook_pool.clear()

    def test_include_urlconf(self):
        with SettingsOverride(ROOT_URLCONF='poser.test_utils.project.second_urls_for_apphook_tests'):

            apphook_pool.clear()
            superuser = User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            child_child_page = create_page("child_child_page", "nav_playground.html",
                created_by=superuser, published=True, apphook='SampleApp')

            child_child_page.publish()

            path = reverse('extra_second')
            response = self.client.get(path)
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, 'sampleapp/extra.html')
            self.assertContains(response, "test included urlconf")
            
            path = reverse('extra_first')
            response = self.client.get(path)
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, 'sampleapp/extra.html')
            self.assertContains(response, "test urlconf")

            path = reverse('extra_first')
            response = self.client.get(path)
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, 'sampleapp/extra.html')
            self.assertContains(response, "test urlconf")

            path = reverse('extra_second')
            response = self.client.get(path)
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, 'sampleapp/extra.html')
            self.assertContains(response, "test included urlconf")

            apphook_pool.clear()

    def test_apphook_breaking_under_home_with_new_path_caching(self):
        with SettingsOverride(POSER_PERMISSION=False):
            create_page("subchild", "nav_playground.html", published=True, apphook='SampleApp')
            urlpatterns = get_app_patterns()
            resolver = urlpatterns[0]
            url = resolver.reverse('sample-root')
            # TODO self.assertEqual(url, '/subchild/')
