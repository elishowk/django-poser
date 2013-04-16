# -*- coding: utf-8 -*-
from __future__ import with_statement
from poser.api import (create_page, publish_page,
   assign_user_to_page)
from poser.test_utils.testcases import SettingsOverrideTestCase
from poser.test_utils.util.context_managers import SettingsOverride

from django.contrib.auth.models import User, Permission, AnonymousUser, Group
from django.contrib.sites.models import Site

class PermissionModeratorTests(SettingsOverrideTestCase):
    """Permissions

    Fixtures contains 3 users and 1 published page and some other stuff

    Users:
        1. `super`: superuser
        2. `master`: user with permissions to all applications
        3. `slave`: user assigned to page `slave-home`

    Pages:
        1. `home`:
            - published page
            - master can do anything on its pages
        2. `master`:
            - published page
            - created by super
            - `master` can do anything on it
        3.       `slave-home`:
                    - not published
                    - assigned slave user which can add/change/delete/
                      move/publish this page

        4. `pageA`:
            - created by super
            - master can add/change/delete on it
    """
    settings_overrides = {
        'POSER_PERMISSION': True,
    }

    def setUp(self):
        # create super user
        self.user_super = User(username="super", is_staff=True, is_active=True,
            is_superuser=True)
        self.user_super.set_password("super")
        self.user_super.save()
        # create staff user
        self.user_staff = User(username="staff", is_staff=True, is_active=True)
        self.user_staff.set_password("staff")
        self.user_staff.save()

        with self.login_user_context(self.user_super):

            self._home_page = create_page("home", "nav_playground.html",
                                         created_by=self.user_super)

            # master page & master user


            # create master user
            master = User(username="master", email="master@django-poser.org", is_staff=True, is_active=True)
            master.set_password('master')
            master.save()
            self._master_page = create_page("home", "nav_playground.html",
                                         created_by=master)

            self.user_master = master
            # create non global, non staff user
            self.user_non_global = User(username="nonglobal", is_active=True)
            self.user_non_global.set_password("nonglobal")
            self.user_non_global.save()

            # slave page & slave user

            self._slave_page = create_page("slave-home", "nav_playground.html",
                              created_by=self.user_super)

            slave = User(username='slave', email='slave@django-poser.org', is_staff=True)
            slave.set_password('slave')
            slave.save()

            self.user_slave = slave

            assign_user_to_page(self.slave_page, self.user_slave, grant_all=True)

            # create page_b
            page_b = create_page("pageB", "nav_playground.html", created_by=self.user_super)
            # Normal user
            normal = User(username='normal', email='normal@django-poser.org', is_active=True)
            normal.set_password('normal')
            normal.save()
            self.user_normal = normal
            # it's allowed for the normal user to view the page
            assign_user_to_page(page_b, self.user_normal, can_view=True)
            self.user_normal = self.reload(self.user_normal)
            # create page_a - sample page from master

            page_a = create_page("pageA", "nav_playground.html",
                                 created_by=self.user_super)
            assign_user_to_page(page_a, self.user_master,
                can_add=True, can_change=True, can_delete=True, can_publish=True)

            # publish after creating all get_query_set
            publish_page(self.home_page, self.user_super)

            publish_page(self.master_page, self.user_super)

            self.page_b = publish_page(page_b, self.user_super)

    @property
    def master_page(self):
        return self.reload(self._master_page)

    @property
    def slave_page(self):
        return self.reload(self._slave_page)

    @property
    def home_page(self):
        return self.reload(self._home_page)

    #def test_super_can_add_page_to_root(self):
    #    with self.login_user_context(self.user_super):
    #        response = self.client.get(URL_POSER_PAGE_ADD)
    #        self.assertEqual(response.status_code, 200)
    #
    #def test_master_can_add_page_to_root(self):
    #    with self.login_user_context(self.user_master):
    #        response = self.client.get(URL_POSER_PAGE_ADD)
    #        self.assertEqual(response.status_code, 403)
    #
    #def test_slave_can_add_page_to_root(self):
    #    with self.login_user_context(self.user_slave):
    #        response = self.client.get(URL_POSER_PAGE_ADD)
    #        self.assertEqual(response.status_code, 403)

    def test_same_order(self):
        # create 4 pages
        slugs = []
        for i in range(0, 4):
            page = create_page("page", "nav_playground.html")
            slug = page.slug
            slugs.append(slug)

        # approve last 2 pages in reverse order
        for slug in reversed(slugs[2:]):
            page = publish_page(page, self.user_master)
            #self.check_published_page_attributes(page)

    def test_create_copy_publish(self):
        # create new page to copy
        page = create_page("page", "nav_playground.html")

        with self.login_user_context(self.user_master):
            copied_page = page.copy_page(self.home_page, page.site, True, True)

        page = publish_page(copied_page, self.user_master)
        #self.check_published_page_attributes(page)


    def test_create_publish_copy(self):
        # create new page to copy
        page = create_page("page", "nav_playground.html")

        page = publish_page(page, self.user_master)

        with self.login_user_context(self.user_master):
            copied_page = page.copy_page(self.master_page, page.site, True, True)

        #self.check_published_page_attributes(page)
        copied_page = publish_page(copied_page, self.user_master)
        #self.check_published_page_attributes(copied_page)

    def test_superuser_can_view(self):
        url = self.page_b.get_absolute_url()
        with self.login_user_context(self.user_super):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_staff_can_view(self):
        url = self.page_b.get_absolute_url()
        login_ok = self.client.login(username=self.user_staff.username, password=self.user_staff.username)
        self.assertTrue(login_ok)
        # really logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        login_user_id = self.client.session.get('_auth_user_id')
        user = User.objects.get(username=self.user_staff.username)
        self.assertEquals(login_user_id,user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_normal_can_view(self):
        url = self.page_b.get_absolute_url()
        with self.login_user_context(self.user_normal):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        with self.login_user_context(self.user_non_global):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
        with SettingsOverride(POSER_PUBLIC_FOR=None):
            # non logged in user
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

    def test_anonymous_user_public_for_all(self):
        url = self.page_b.get_absolute_url()
        with SettingsOverride(POSER_PUBLIC_FOR='all'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_anonymous_user_public_for_none(self):
        # default of when to show pages to anonymous user doesn't take
        # global permissions into account
        url = self.page_b.get_absolute_url()
        with SettingsOverride(POSER_PUBLIC_FOR=None):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)


class PatricksMoveTest(SettingsOverrideTestCase):
    """
    Fixtures contains 3 users and 1 published page and some other stuff

    Users:
        1. `super`: superuser
        2. `master`: user with permissions to all applications
        3. `slave`: user assigned to page `slave-home`

    Pages:
        1. `home`:
            - published page
            - master can do anything on its subpages, but not on home!

        2. `master`:
            - published page
            - crated by super
            - `master` can do anything on it and its descendants
            - subpages:

        3.       `slave-home`:
                    - not published
                    - assigned slave user which can add/change/delete/
                      move/publish/moderate this page and its descendants
                    - `master` user want to moderate this page and all descendants

        4. `pageA`:
            - created by super
            - master can add/change/delete on it and descendants
    """
    settings_overrides = {
        'POSER_PERMISSION': True,
    }

    def setUp(self):
        # create super user
        self.user_super = User(username="super", is_staff=True, is_active=True,
            is_superuser=True)
        self.user_super.set_password("super")
        self.user_super.save()
        with self.login_user_context(self.user_super):

            self._home_page = create_page("home", "nav_playground.html",
                                         created_by=self.user_super)


            # create master user
            master = User.objects.create(username="master", email="master@django-poser.org", password="master")
            self.user_master = master
            # master page & master user
            self._master_page = create_page("master", "nav_playground.html", created_by=master)

            # assign master user under home page
            assign_user_to_page(self.home_page, self.user_master,
                                grant_all=True)

            # and to master page
            assign_user_to_page(self.master_page, self.user_master, grant_all=True)

            # slave page & slave user

            self._slave_page = create_page("slave-home", "nav_playground.html",
                              created_by=self.user_super)
            slave = User(username='slave', email='slave@django-poser.org', is_staff=True, is_active=True)
            slave.set_password('slave')
            slave.save()
            self.user_slave = slave
            assign_user_to_page(self.slave_page, self.user_slave, grant_all=True)

            # create page_a - sample page from master

            page_a = create_page("pageA", "nav_playground.html",
                                 created_by=self.user_super)
            assign_user_to_page(page_a, self.user_master,
                can_add=True, can_change=True, can_delete=True, can_publish=True)

            # publish after creating all get_query_set
            publish_page(self.home_page, self.user_super)
            publish_page(self.master_page, self.user_super)

        with self.login_user_context(self.user_slave):

            # all of them are under moderation...
            self._pa = create_page("pa", "nav_playground.html")
            self._pb = create_page("pb", "nav_playground.html")
            self._pc = create_page("pc", "nav_playground.html")

            self._pd = create_page("pd", "nav_playground.html")
            self._pe = create_page("pe", "nav_playground.html")

            self._pf = create_page("pf", "nav_playground.html")
            self._pg = create_page("pg", "nav_playground.html")
            self._ph = create_page("ph", "nav_playground.html")

            # login as master for approval
            publish_page(self.slave_page, self.user_master)

            # publish and approve them all
            publish_page(self.pa, self.user_master)
            publish_page(self.pb, self.user_master)
            publish_page(self.pc, self.user_master)
            publish_page(self.pd, self.user_master)
            publish_page(self.pe, self.user_master)
            publish_page(self.pf, self.user_master)
            publish_page(self.pg, self.user_master)
            publish_page(self.ph, self.user_master)

    @property
    def master_page(self):
        return self.reload(self._master_page)

    @property
    def slave_page(self):
        return self.reload(self._slave_page)

    @property
    def home_page(self):
        return self.reload(self._home_page)

    @property
    def pa(self):
        return self.reload(self._pa)

    @property
    def pb(self):
        return self.reload(self._pb)

    @property
    def pc(self):
        return self.reload(self._pc)

    @property
    def pd(self):
        return self.reload(self._pd)

    @property
    def pe(self):
        return self.reload(self._pe)

    @property
    def pf(self):
        return self.reload(self._pf)

    @property
    def pg(self):
        return self.reload(self._pg)

    @property
    def ph(self):
        return self.reload(self._ph)


class ViewPermissionTests(SettingsOverrideTestCase):
    settings_overrides = {
        'POSER_PERMISSION': True,
        'POSER_PUBLIC_FOR': 'all',
    }


    def get_request(self, user=None):
        attrs = {
            'user': user or AnonymousUser(),
            'REQUEST': {},
            'session': {},
        }
        return type('Request', (object,), attrs)

    def test_public_for_all_staff(self):
        request = self.get_request()
        page = create_page("test-public-for-all", "nav_playground.html")
        self.assertTrue(page.has_view_permission(request))

    def test_public_for_all_staff_assert_num_queries(self):
        request = self.get_request()
        page = create_page("test-public-for-all", "nav_playground.html")
        with self.assertNumQueries(0):
            page.has_view_permission(request)

    def test_public_for_all(self):
        with SettingsOverride(POSER_PUBLIC_FOR='all'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            request = self.get_request(user)
            page = create_page("test-public-for-all", "nav_playground.html")
            self.assertTrue(page.has_view_permission(request))

    def test_public_for_all_num_queries(self):
        with SettingsOverride(POSER_PUBLIC_FOR='all'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            request = self.get_request(user)
            page = create_page("test-public-for-all", "nav_playground.html")
            with self.assertNumQueries(0):
                page.has_view_permission(request)

    def test_unauthed(self):
        with SettingsOverride(POSER_PUBLIC_FOR='all'):
            request = self.get_request()
            page = create_page("test-public-for-all", "nav_playground.html")
            self.assertTrue(page.has_view_permission(request))

    def test_unauthed_num_queries(self):
        with SettingsOverride(POSER_PUBLIC_FOR='all'):
            request = self.get_request()
            site = Site()
            site.pk = 1
            page = create_page("test-public-for-all", "nav_playground.html")
            with self.assertNumQueries(0):
                page.has_view_permission(request)

    def test_authed_basic_perm(self):
        with SettingsOverride(POSER_PUBLIC_FOR='staff'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            user.user_permissions.add(Permission.objects.get(codename="view_page"))
            user.save()
            request = self.get_request(user)
            page = create_page("test-public-for-all", "nav_playground.html")
            self.assertTrue(page.has_view_permission(request))

    def test_authed_basic_perm_num_queries(self):
        with SettingsOverride(POSER_PUBLIC_FOR='staff'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            user.user_permissions.add(Permission.objects.get(codename="view_page"))
            user.save()
            request = self.get_request(user)
            page = create_page("test-public-for-all", "nav_playground.html")
            with self.assertNumQueries(0):
                """
                The queries are:
                Generic django permission lookup
                content type lookup by permission lookup
                """
                page.has_view_permission(request)

    def test_authed_no_access(self):
        with SettingsOverride(POSER_PUBLIC_FOR='staff'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            request = self.get_request(user)
            page = create_page("test-public-for-all", "nav_playground.html")
            self.assertFalse(page.has_view_permission(request))

    def test_unauthed_no_access(self):
        with SettingsOverride(POSER_PUBLIC_FOR='staff'):
            request = self.get_request()
            page = create_page("test-public-for-all", "nav_playground.html")
            self.assertFalse(page.has_view_permission(request))

    def test_unauthed_no_access_num_queries(self):
        request = self.get_request()
        page = create_page("test-public-for-all", "nav_playground.html")
        with self.assertNumQueries(0):
            page.has_view_permission(request)

    def test_page_permissions(self):
        with SettingsOverride(POSER_PUBLIC_FOR='staff'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            user.user_permissions.add(Permission.objects.get(codename="view_page"))
            user.save()
            request = self.get_request(user)
            page = create_page('A', 'nav_playground.html')
            self.assertTrue(page.has_view_permission(request))

    def test_page_permissions_view_groups(self):
        with SettingsOverride(POSER_PUBLIC_FOR='staff'):
            user = User.objects.create_user('user', 'user@domain.com', 'user')
            group = Group.objects.create(name='testgroup')
            group.user_set.add(user)
            request = self.get_request(user)
            page = create_page('A', 'nav_playground.html')
            assign_user_to_page(page, group, grant_all=True)
            self.assertTrue(page.has_view_permission(request))
