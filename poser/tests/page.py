# -*- coding: utf-8 -*-
from __future__ import with_statement
from poser.api import create_page
from poser.models import Page
from poser.test_utils.testcases import POSERTestCase
from poser.test_utils.util.context_managers import SettingsOverride
from poser.utils.page_resolver import get_page_from_request, is_valid_url
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
import datetime
import os.path
from poser.utils.page import is_valid_page_slug


class PagesTestCase(POSERTestCase):

    #def test_add_page(self):
    #    """
    #    Test that the add admin page could be displayed via the admin
    #    """
    #    superuser = self.get_superuser()
    #    with self.login_user_context(superuser):
    #        response = self.client.get(URL_POSER_PAGE_ADD)
    #        self.assertEqual(response.status_code, 200)

   #def test_create_page(self):
   #    """
   #    Test that a page can be created via the admin
   #    """
   #    page_data = self.get_new_page_data()

   #    superuser = self.get_superuser()
   #    with self.login_user_context(superuser):
   #        response = self.client.post(URL_POSER_PAGE_ADD, page_data)
   #        page = Page.objects.get(slug=page_data['slug'])
   #        self.assertNotEqual(page.title, None)
   #        page.published = True
   #        page.save()
   #        self.assertEqual(page.get_title(), page_data['title'])
   #        self.assertEqual(page.get_slug(), page_data['slug'])
   #        self.assertEqual(page.placeholders.all().count(), 2)
   #
   #        # were public instanes created?
   #        page = Page.objects.get_query_set().get(slug=page_data['slug'])


   # def test_slug_collision(self):
   #     """
   #     Test a slug collision
   #     """
   #     page_data = self.get_new_page_data()
   #     # create first page
   #     superuser = self.get_superuser()
   #     with self.login_user_context(superuser):
   #         response = self.client.post(URL_POSER_PAGE_ADD, page_data)
   #         self.assertRedirects(response, URL_POSER_PAGE)
   #         # create page with the same page_data
   #         response = self.client.post(URL_POSER_PAGE_ADD, page_data)
   #
   #         if settings.i18n_installed:
   #             self.assertEqual(response.status_code, 302)
   #             # did we got right redirect?
   #             self.assertEqual(response['Location'].endswith(URL_POSER_PAGE), True)
   #         else:
   #             self.assertEqual(response.status_code, 200)
   #             self.assertEqual(response['Location'].endswith(URL_POSER_PAGE_ADD), True)
   #         # TODO: check for slug collisions after move
   #         # TODO: check for slug collisions with different settings

    def test_slug_collisions_api_1(self):
        """ Checks for slug collisions on sibling pages - uses API to create pages
        """
        page1_1 = create_page('test page 1_1', 'nav_playground.html',
                                published=True, slug="foo")
        page1_2 = create_page('test page 1_2', 'nav_playground.html',
                                published=True, slug="foo")
        # both sibling pages has same slug, so both pages has an invalid slug
        self.assertFalse(is_valid_page_slug(page1_1,
            page1_1.get_slug(), page1_1.site))
        self.assertFalse(is_valid_page_slug(page1_2,
            page1_2.get_slug(), page1_2.site))

    def test_details_view(self):
        """
        Test the details view
        """
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.get(self.get_pages_root())
            self.assertEqual(response.status_code, 404)
            page = create_page('test page 1', "nav_playground.html")
            response = self.client.get(self.get_pages_root())
            self.assertEqual(response.status_code, 404)
            self.assertTrue(page.publish())
            page2 = create_page("test page 2", "nav_playground.html",
                                    published=True)
            response = self.client.get(page2.get_absolute_url())
            self.assertEqual(response.status_code, 200)

   # def test_edit_page(self):
   #     """
   #     Test that a page can edited via the admin
   #     """
   #     superuser = self.get_superuser()
   #     with self.login_user_context(superuser):
   #         page_data = self.get_new_page_data()
   #         response = self.client.post(URL_POSER_PAGE_ADD, page_data)
   #         page = Page.objects.get(slug=page_data['slug'])
   #         response = self.client.get('/admin/poser/page/%s/' %page.id)
   #         self.assertEqual(response.status_code, 200)
   #         page_data['title'] = 'changed title'
   #         response = self.client.post('/admin/poser/page/%s/' %page.id, page_data)
   #         self.assertRedirects(response, URL_POSER_PAGE)
   #         self.assertEqual(page.get_title(), 'changed title')


    #def test_meta_description_and_keywords_fields_from_admin(self):
    #    """
    #    Test that description and keywords tags can be set via the admin
    #    """
    #    superuser = self.get_superuser()
    #    with self.login_user_context(superuser):
    #        page_data = self.get_new_page_data()
    #        page_data["meta_description"] = "I am a page"
    #        page_data["meta_keywords"] = "page,poser,stuff"
    #        response = self.client.post(URL_POSER_PAGE_ADD, page_data)
    #        page =  Page.objects.get(slug=page_data['slug'])
    #        response = self.client.get('/admin/poser/page/%s/' %page.id)
    #        self.assertEqual(response.status_code, 200)
    #        page_data['meta_description'] = 'I am a duck'
    #        response = self.client.post('/admin/poser/page/%s/' %page.id, page_data)
    #        self.assertRedirects(response, URL_POSER_PAGE)
    #        page = Page.objects.get(slug=page_data["slug"])
    #        self.assertEqual(page.get_meta_description(), 'I am a duck')
    #        self.assertEqual(page.get_meta_keywords(), 'page,poser,stuff')

    #def test_meta_description_and_keywords_from_template_tags(self):
    #    from django import template
    #    superuser = self.get_superuser()
    #    with self.login_user_context(superuser):
    #        page_data = self.get_new_page_data()
    #        page_data["title"] = "Hello"
    #        page_data["meta_description"] = "I am a page"
    #        page_data["meta_keywords"] = "page,poser,stuff"
    #        self.client.post(URL_POSER_PAGE_ADD, page_data)
    #        page =  Page.objects.get(slug=page_data['slug'])
    #        self.client.post('/admin/poser/page/%s/' %page.id, page_data)
    #        t = template.Template("{% load  %}{% page_attribute title %} {% page_attribute meta_description %} {% page_attribute meta_keywords %}")
    #        req = HttpRequest()
    #        page.published = True
    #        page.save()
    #        req.current_page = page
    #        req.REQUEST = {}
    #        self.assertEqual(t.render(template.Context({"request": req})), "Hello I am a page page,poser,stuff")


    def test_copy_page(self):
        """
        Test that a page can be copied via its model
        """
        page_a = create_page("page_a", "nav_playground.html")
        create_page("page_a_a_a", "nav_playground.html")

        page_b = create_page("page_b", "nav_playground.html")

        count = Page.objects.get_query_set().count()

        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            page_a.copy_page(page_b, page_a.site)

        self.assertEqual(Page.objects.get_query_set().count() - count, 1)

    def test_templates(self):
        """
        Test the inheritance magic for templates
        """
        template = "nav_playground.html"
        child = create_page("child", template)
        grand_child = create_page("child", template)
        child.save()
        grand_child.save()
        self.assertEqual(child.template, template)
        grand_child.get_template()

   # def test_get_page_from_request_on_non_poser_admin(self):
   #         request = self.get_request(
   #         reverse('admin:sampleapp_category_change', args=(1,))
   #     )
   #     page = get_page_from_request(request)
   #     self.assertEqual(page, None)

    #def test_get_page_from_request_on_poser_admin(self):
    #    page = create_page("page", "nav_playground.html", "en")
    #    request = self.get_request(
    #        reverse('admin:poser_page_change', args=(page.pk,))
    #    )
    #    found_page = get_page_from_request(request)
    #    self.assertTrue(found_page)
    #    self.assertEqual(found_page.pk, page.pk)

    #def test_get_page_from_request_on_poser_admin_nopage(self):
    #    request = self.get_request(
    #        reverse('admin:poser_page_change', args=(1,))
    #    )
    #    page = get_page_from_request(request)
    #    self.assertEqual(page, None)

    def test_get_page_from_request_cached(self):
        mock_page = 'hello world'
        request = self.get_request(
            reverse('admin:sampleapp_category_change', args=(1,))
        )
        request._current_page_cache = mock_page
        page = get_page_from_request(request)
        self.assertEqual(page, mock_page)

    def test_get_page_from_request_nopage(self):
        request = self.get_request('/')
        page = get_page_from_request(request)
        self.assertEqual(page, None)

    def test_get_page_from_request_with_page_404(self):
        page = create_page("page", "nav_playground.html", published=True)
        page.publish()
        request = self.get_request('/does-not-exist/')
        found_page = get_page_from_request(request)
        self.assertEqual(found_page, None)

    def test_get_page_without_final_slash(self):
        root = create_page("root", "nav_playground.html", slug="root",
                           published=True)
        page = create_page("page", "nav_playground.html", slug="page",
                           published=True)
        root.publish()
        page.publish()
        request = self.get_request('/page')
        found_page = get_page_from_request(request)
        self.assertFalse(found_page is None)

    def test_get_page_from_request_with_page_preview(self):
        page = create_page("page", "nav_playground.html")
        request = self.get_request('%s?preview' % page.get_absolute_url())
        request.user.is_staff = False
        found_page = get_page_from_request(request)
        self.assertEqual(found_page, None)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            request = self.get_request('%s?preview&draft' % page.get_absolute_url())
            found_page = get_page_from_request(request)
            self.assertTrue(found_page)
            self.assertEqual(found_page.pk, page.pk)

    def test_page_already_expired(self):
        """
        Test that a page which has a end date in the past gives a 404, not a
        500.
        """
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        with SettingsOverride(POSER_MODERATOR=False, POSER_PERMISSION=False):
            page = create_page('page', 'nav_playground.html',
                               publication_end_date=yesterday, published=True)
            resp = self.client.get(page.get_absolute_url())
            self.assertEqual(resp.status_code, 404)

    #def test_existing_overwrite_url(self):
    #    with SettingsOverride(POSER_MODERATOR=False, POSER_PERMISSION=False):
    #        create_page('home', 'nav_playground.html', published=True)
    #        create_page('boo', 'nav_playground.html', published=True)
    #        data = {
    #            'title': 'foo',
    #            'overwrite_url': '/boo/',
    #            'slug': 'foo',
    #            'template': 'nav_playground.html',
    #            'site': 1,
    #        }
    #        form = PageForm(data)
    #        self.assertFalse(form.is_valid())
    #        self.assertTrue('overwrite_url' in form.errors)

    def test_page_urls(self):
        page1 = create_page('test page 1', 'nav_playground.html',
            published=True)

        page2 = create_page('test page 2', 'nav_playground.html',
            published=True)

        page3 = create_page('test page 3', 'nav_playground.html',
            published=True)

        page4 = create_page('test page 4', 'nav_playground.html',
            published=True)

        page5 = create_page('test page 5', 'nav_playground.html',
            published=True)

        self.assertEqual(page1.get_absolute_url(),
            self.get_pages_root()+'test-page-1/')
        self.assertEqual(page2.get_absolute_url(),
            self.get_pages_root()+'test-page-2/')
        self.assertEqual(page4.get_absolute_url(),
            self.get_pages_root()+'test-page-4/')

        page3 = page3.move_page(page1)
        self.assertEqual(page3.get_absolute_url(),
            self.get_pages_root()+'test-page-1-copy/')

        page5 = page5.move_page(page2)
        self.assertEqual(page5.get_absolute_url(),
            self.get_pages_root()+'test-page-2-copy/')

        page3 = page3.move_page(page4)
        self.assertEqual(page3.get_absolute_url(),
            self.get_pages_root()+'test-page-4-copy/')

    def test_page_overwrite_urls(self):
        page2 = create_page('test page 2', 'nav_playground.html',
            published=True)

        page3 = create_page('test page 3', 'nav_playground.html',
            published=True, overwrite_url='i-want-another-url')

        self.assertEqual(page2.get_absolute_url(),
            self.get_pages_root()+'test-page-2/')
        self.assertEqual(page3.get_absolute_url(),
            self.get_pages_root()+'i-want-another-url/')

        page2 = Page.objects.get(pk=page2.pk)
        page3 = Page.objects.get(pk=page3.pk)

        self.assertEqual(page2.get_absolute_url(),
            self.get_pages_root()+'test-page-2/')
        self.assertEqual(page3.get_absolute_url(),
            self.get_pages_root()+'i-want-another-url/')

        # tests a bug found in 2.2 where saving an ancestor page
        # wiped out the overwrite_url for child pages
        page2.save()
        self.assertEqual(page3.get_absolute_url(),
            self.get_pages_root()+'i-want-another-url/')

    def test_slug_url_overwrite_clash(self):
        """ Tests if a URL-Override clashes with a normal page url
        """
        with SettingsOverride(POSER_PERMISSION=False):
            bar = create_page('bar', 'nav_playground.html', published=False)
            foo = create_page('foo', 'nav_playground.html', published=True)
            # Tests to assure is_valid_url is ok on plain pages
            self.assertTrue(is_valid_url(bar.get_absolute_url(), bar))
            self.assertTrue(is_valid_url(foo.get_absolute_url(), foo))

            # Set url_overwrite for page foo
            foo.has_url_overwrite = True
            foo.path = '/bar/'
            foo.save()
            try:
                url = is_valid_url(bar.get_absolute_url(),bar)
            except ValidationError:
                url = False
            if url:
                bar.published = True
                bar.save()
            self.assertFalse(bar.published)

    def test_valid_url_multisite(self):
        site1 = Site.objects.get_current()
        site3 = Site.objects.create(domain="sample3.com", name="sample3.com")
        bar = create_page('bar', 'nav_playground.html', slug="bar", published=True, site=site1)
        bar_s3 = create_page('bar', 'nav_playground.html', slug="bar", published=True, site=site3)

        self.assertTrue(is_valid_url(bar.get_absolute_url(), bar))
        self.assertTrue(is_valid_url(bar_s3.get_absolute_url(), bar_s3))

    def test_home_slug_not_accessible(self):
        with SettingsOverride(POSER_PERMISSION=False):
            page = create_page('page', 'nav_playground.html', published=True)
            self.assertEqual(page.get_absolute_url(), '/page/')
            resp = self.client.get('/')
            self.assertEqual(resp.status_code, HttpResponseNotFound.status_code)
            resp = self.client.get('/page/')
            self.assertEqual(resp.status_code, HttpResponse.status_code)


class NoAdminPageTests(POSERTestCase):
    urls = 'poser.test_utils.project.noadmin_urls'

    def setUp(self):
        admin = 'django.contrib.admin'
        noadmin_apps = [app for app in settings.INSTALLED_APPS if not app == admin]
        self._ctx = SettingsOverride(INSTALLED_APPS=noadmin_apps)
        self._ctx.__enter__()

    def tearDown(self):
        self._ctx.__exit__(None, None, None)

    def test_get_page_from_request_fakeadmin_nopage(self):
        request = self.get_request('/admin/')
        page = get_page_from_request(request)
        self.assertEqual(page, None)

