# -*- coding: utf-8 -*-
from __future__ import with_statement
from poser.test_utils.testcases import POSERTestCase
from poser.test_utils.util.context_managers import SettingsOverride
from poser.utils import urlutils


class UrlutilsTestCase(POSERTestCase):
    def test_levelize_path(self):
        path = '/application/item/new'
        output = ['/application/item/new', '/application/item', '/application']
        self.assertEqual(urlutils.levelize_path(path), output)
        
    def test_urljoin(self):
        self.assertEqual('a/b/c/', urlutils.urljoin('a', 'b', 'c'))
        self.assertEqual('a/b/c/', urlutils.urljoin('a', '//b//', 'c'))
        self.assertEqual('a/', urlutils.urljoin('a', ''))

    def test_is_media_url(self):
        with SettingsOverride(MEDIA_URL='/media/'):
            request = self.get_request('/media/')
            self.assertTrue(urlutils.is_media_request(request))
            request = self.get_request('/no-media/')
            self.assertFalse(urlutils.is_media_request(request))
        with SettingsOverride(MEDIA_URL='http://testserver2.com/'):
            request = self.get_request('/')
            self.assertFalse(urlutils.is_media_request(request))
        with SettingsOverride(MEDIA_URL='http://testserver/media/'):
            request = self.get_request('/media/')
            self.assertTrue(urlutils.is_media_request(request))
            request = self.get_request('/no-media/')
            self.assertFalse(urlutils.is_media_request(request))
