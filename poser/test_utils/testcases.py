# -*- coding: utf-8 -*-
from poser.test_utils.util.context_managers import (UserLoginContext, 
    SettingsOverride)
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template.context import Context
from django.test import testcases
from django.test.client import Client, RequestFactory
import sys
import urllib
import warnings


class _Warning(object):
    def __init__(self, message, category, filename, lineno):
        self.message = message
        self.category = category
        self.filename = filename
        self.lineno = lineno


def _collectWarnings(observeWarning, f, *args, **kwargs):
    def showWarning(message, category, filename, lineno, file=None, line=None):
        assert isinstance(message, Warning)
        observeWarning(_Warning(
                message.args[0], category, filename, lineno))

    # Disable the per-module cache for every module otherwise if the warning
    # which the caller is expecting us to collect was already emitted it won't
    # be re-emitted by the call to f which happens below.
    for v in sys.modules.itervalues():
        if v is not None:
            try:
                v.__warningregistry__ = None
            except:
                # Don't specify a particular exception type to handle in case
                # some wacky object raises some wacky exception in response to
                # the setattr attempt.
                pass

    origFilters = warnings.filters[:]
    origShow = warnings.showwarning
    warnings.simplefilter('always')
    try:
        warnings.showwarning = showWarning
        result = f(*args, **kwargs)
    finally:
        warnings.filters[:] = origFilters
        warnings.showwarning = origShow
    return result


class POSERTestCase(testcases.TestCase):
    counter = 1

    def _fixture_setup(self):
        super(POSERTestCase, self)._fixture_setup()
        self.create_fixtures()
        self.client = Client()

    def create_fixtures(self):
        pass

    def _post_teardown(self):
        # Needed to clean the menu keys cache, see menu.menu_pool.clear()
        super(POSERTestCase, self)._post_teardown()

    def login_user_context(self, user):
        return UserLoginContext(self, user)

    def get_superuser(self):
        try:
            admin = User.objects.get(username="admin")
        except User.DoesNotExist:
            admin = User(username="admin", is_staff=True, is_active=True, is_superuser=True)
            admin.set_password("admin")
            admin.save()
        return admin

    def get_staff_user_with_no_permissions(self):
        """
        Used in security tests
        """
        staff = User(username="staff", is_staff=True, is_active=True)
        staff.set_password("staff")
        staff.save()
        return staff

    def get_new_page_data(self, parent_id=''):
        page_data = {
            'title': 'test page %d' % self.counter,
            'slug': 'test-page-%d' % self.counter,
            'template': 'nav_playground.html',
            'site': 1,
        }
        # required only if user haves can_change_permission
        page_data['pagepermission_set-TOTAL_FORMS'] = 0
        page_data['pagepermission_set-INITIAL_FORMS'] = 0
        page_data['pagepermission_set-MAX_NUM_FORMS'] = 0
        page_data['pagepermission_set-2-TOTAL_FORMS'] = 0
        page_data['pagepermission_set-2-INITIAL_FORMS'] = 0
        page_data['pagepermission_set-2-MAX_NUM_FORMS'] = 0
        self.counter = self.counter + 1
        return page_data

    def print_page_structure(self, qs):
        """Just a helper to see the page struct.
        """
        for page in qs:
            ident = "  " * page.level
            print "%s%s (%s)" % (ident, page,
                                    page.pk)

    def print_node_structure(self, nodes, *extra):
        def _rec(nodes, level=0):
            ident = level * '  '
            for node in nodes:
                raw_attrs = [(bit, getattr(node, bit, node.attr.get(bit, "unknown"))) for bit in extra]
                attrs = ', '.join(['%s: %r' % data for data in raw_attrs])
                print "%s%s: %s" % (ident, node.title, attrs)
                _rec(node.children, level + 1)
        _rec(nodes)

    def assertObjectExist(self, qs, **filter):
        try:
            return qs.get(**filter)
        except ObjectDoesNotExist:
            pass
        raise self.failureException, "ObjectDoesNotExist raised"

    def assertObjectDoesNotExist(self, qs, **filter):
        try:
            qs.get(**filter)
        except ObjectDoesNotExist:
            return
        raise self.failureException, "ObjectDoesNotExist not raised"

    def move_page(self, page, target_page, position="first-child"):
        page.move_page(target_page, position)
        return self.reload_page(page)

    def reload_page(self, page):
        """
        Returns a fresh instance of the page from the database
        """
        return self.reload(page)

    def reload(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)

    def get_pages_root(self):
        return urllib.unquote(reverse("pages-root"))

    def get_context(self, path=None):
        if not path:
            path = self.get_pages_root()
        context = {}
        request = self.get_request(path)
        context['request'] = request
        return Context(context)

    def get_request(self, path=None, post_data=None, enforce_csrf_checks=False):
        factory = RequestFactory()

        if not path:
            path = self.get_pages_root()

        if post_data:
            request = factory.post(path, post_data)
        else:
            request = factory.get(path)
        request.session = self.client.session
        request.user = getattr(self, 'user', AnonymousUser())
        request._dont_enforce_csrf_checks = not enforce_csrf_checks
        return request

    def failUnlessWarns(self, category, message, f, *args, **kwargs):
        warningsShown = []
        result = _collectWarnings(warningsShown.append, f, *args, **kwargs)

        if not warningsShown:
            self.fail("No warnings emitted")
        first = warningsShown[0]
        for other in warningsShown[1:]:
            if ((other.message, other.category)
                != (first.message, first.category)):
                self.fail("Can't handle different warnings")
        self.assertEqual(first.message, message)
        self.assertTrue(first.category is category)

        return result
    assertWarns = failUnlessWarns


class SettingsOverrideTestCase(POSERTestCase):
    settings_overrides = {}

    def _pre_setup(self):
        self._enter_settings_override()
        super(SettingsOverrideTestCase, self)._pre_setup()

    def _enter_settings_override(self):
        self._settings_ctx_manager = SettingsOverride(**self.settings_overrides)
        self._settings_ctx_manager.__enter__()

    def _post_teardown(self):
        super(SettingsOverrideTestCase, self)._post_teardown()
        self._exit_settings_override()

    def _exit_settings_override(self):
        self._settings_ctx_manager.__exit__(None, None, None)
