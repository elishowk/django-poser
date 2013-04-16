from __future__ import with_statement
from poser import __version__
from poser.api import _generate_valid_slug, create_page,\
        assign_user_to_page  # , publish_page
from poser.apphook_pool import apphook_pool
from poser.models.pagemodel import Page
from poser.test_utils.util.context_managers import SettingsOverride
from poser.test_utils.util.mock import AttributeObject
from poser.tests.apphooks import APP_MODULE, APP_NAME
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase
import sys
import json


class PageRESTAPITests(TestCase):

    def setUp(self):
        """
        Sets up a User with the right Page permissions
        """
        super(PageRESTAPITests, self).setUp()
        # Create a user.
        self.username = 'carlos'
        self.password = 'santana'
        self.user = User.objects.create_user(self.username, \
                                             'carlos@santana.com',\
                                             self.password)
        self.user.user_permissions.add(Permission.objects.get(codename="add_page"),\
                                       Permission.objects.get(codename="delete_page"),\
                                       Permission.objects.get(codename="view_page"),\
                                       Permission.objects.get(codename="change_page"))
        self.user.save()
        self.post_data = json.dumps({
            'title': 'Test',
            'template': 'nav_playground.html',
            'apphook': 'SampleApp'
        })
        self.uri = "/pageapi/" + __version__ + "/page/"

    def test_post(self):
        """
        Creates a Page
        """
        response = self.client.post(self.uri, data=self.post_data,\
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(self.uri, data=self.post_data, \
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_list(self):
        """
        Lists user's Pages
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        """
        Creates then GETs a Page
        """
        page = create_page("testget", "nav_playground.html", \
                           apphook="SampleApp", created_by=self.user, published=True)
        published_page = self.client.get("/testget/")
        self.assertEqual(published_page.status_code, 200)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.uri + str(page.id) + "/")
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        """
        Creates then deletes a Page
        """
        page = create_page("test", "nav_playground.html", \
                           apphook="SampleApp", created_by=self.user, published=True)
        self.client.login(username=self.username, password=self.password)
        response = self.client.delete(self.uri + str(page.id) + "/")
        self.assertEqual(response.status_code, 204)
        del_page = self.client.get("/test/")
        self.assertEqual(del_page.status_code, 404)

    def test_put(self):
        """
        Creates then modifies a Page
        """
        page = create_page("testget", "nav_playground.html", \
                           apphook="SampleApp", created_by=self.user, published=True)

        self.client.login(username=self.username, password=self.password)
        response = self.client.put(self.uri + str(page.id) + "/",\
            data=json.dumps(
                {"published": False, "title":"modified"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)
        published_page = self.client.get("/testget/")
        self.assertEqual(published_page.status_code, 404)

    def test_update(self):
        pass


def _grant_page_permission(user, codename):
    content_type = ContentType.objects.get_by_natural_key('poser', 'page')
    perm = Permission.objects.get_or_create(codename='%s_page' % codename,
                                            content_type=content_type)[0]
    user.user_permissions.add(perm)


class PythonAPITests(TestCase):
    def _get_default_create_page_arguments(self):
        return {
            'title': 'Test',
            'template': 'nav_playground.html',
        }

    def test_generate_valid_slug(self):
        title = "Hello Title"
        expected_slug = "hello-title"
        # empty db, it should just slugify
        slug = _generate_valid_slug(title)
        self.assertEqual(slug, expected_slug)

    def test_generage_valid_slug_check_existing(self):
        title = "Hello Title"
        create_page(title, 'nav_playground.html')
        # second time with same title, it should append -1
        expected_slug = "hello-title-1"
        slug = _generate_valid_slug(title)
        self.assertEqual(slug, expected_slug)

    def test_invalid_apphook_type(self):
        self.assertRaises(TypeError, create_page, apphook=1,
                          **self._get_default_create_page_arguments())

    def test_apphook_by_class(self):
        if APP_MODULE in sys.modules:
            del sys.modules[APP_MODULE]
        apphooks = (
            '%s.%s' % (APP_MODULE, APP_NAME),
        )

        with SettingsOverride(POSER_APPHOOKS=apphooks):
            apphook_pool.clear()
            apphook = apphook_pool.get_apphook(APP_NAME)
            page = create_page(apphook=apphook,
                               **self._get_default_create_page_arguments())
            self.assertEqual(page.get_application_urls(), APP_NAME)

    def test_invalid_dates(self):
        self.assertRaises(AssertionError, create_page, publication_date=1,
                          **self._get_default_create_page_arguments())
        self.assertRaises(AssertionError, create_page, publication_end_date=1,
                          **self._get_default_create_page_arguments())

    def test_assign_user_to_page_nothing(self):
        page = create_page(**self._get_default_create_page_arguments())
        user = User.objects.create(username='user', email='user@django-poser.org',
                                   is_staff=True, is_active=True)
        request = AttributeObject(user=user)
        self.assertFalse(page.has_change_permission(request))

    def test_assign_user_to_page_single(self):
        page = create_page(**self._get_default_create_page_arguments())
        user = User.objects.create(username='user', email='user@django-poser.org',
                                   is_staff=True, is_active=True)
        request = AttributeObject(user=user)
        assign_user_to_page(page, user, can_change=True)
        self.assertFalse(page.has_change_permission(request))
        self.assertFalse(page.has_add_permission(request))
        _grant_page_permission(user, 'change')
        page = Page.objects.get(pk=page.pk)
        user = User.objects.get(pk=user.pk)
        request = AttributeObject(user=user)
        self.assertTrue(page.has_change_permission(request))
        self.assertFalse(page.has_add_permission(request))

    def test_assign_user_to_page_all(self):
        page = create_page(**self._get_default_create_page_arguments())
        user = User.objects.create(username='user', email='user@django-poser.org',
                                   is_staff=True, is_active=True)
        request = AttributeObject(user=user)
        assign_user_to_page(page, user, grant_all=True)
        self.assertFalse(page.has_change_permission(request))
        self.assertTrue(page.has_add_permission(request))
        _grant_page_permission(user, 'change')
        _grant_page_permission(user, 'add')
        page = Page.objects.get(pk=page.pk)
        user = User.objects.get(pk=user.pk)
        request = AttributeObject(user=user)
        self.assertTrue(page.has_change_permission(request))
        self.assertTrue(page.has_add_permission(request))

    def test_page_overwrite_url_default(self):
        page = create_page(**self._get_default_create_page_arguments())
        self.assertFalse(page.has_url_overwrite)
        self.assertEqual(page.get_path(), 'test')

    def test_create_page_can_overwrite_url(self):
        page_attrs = self._get_default_create_page_arguments()
        page_attrs["overwrite_url"] = 'test/home'
        page = create_page(**page_attrs)
        self.assertTrue(page.has_url_overwrite)
        self.assertEqual(page.get_path(), 'test/home')
