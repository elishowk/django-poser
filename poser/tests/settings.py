# -*- coding: utf-8 -*-
from __future__ import with_statement
from poser.conf.patch import post_patch_check
from poser.test_utils.testcases import POSERTestCase
from poser.test_utils.util.context_managers import SettingsOverride
from django.core.exceptions import ImproperlyConfigured

class SettingsTests(POSERTestCase):
    def test_poser_templates_length(self):
        '''
        Ensure that the correct exception is raised when POSER_TEMPLATES is
        configured with an empty tuple or the magic value 'INHERIT'
        '''
        improperly_configured_template_tests = (
            # don't allow 0 length
            (),
        )
        for value_to_test in improperly_configured_template_tests:
            with SettingsOverride(DEBUG=True, POSER_TEMPLATES=value_to_test):
                self.assertRaises(ImproperlyConfigured, post_patch_check)

    def test_poser_templates_none(self):
        '''
        In fixing #814, POSER_TEMPLATES default after patching changes from None
        to an empty tuple. As such, If the user has decided to set None for some
        reason, this test lets us know what to expect.
        As it stands, we should get a TypeError because post_patch attempts to
        turn None into a tuple explicitly.
        '''

        with SettingsOverride(DEBUG=True, POSER_TEMPLATES=None):
            self.assertRaises(ImproperlyConfigured, post_patch_check)
            

    def test_poser_templates_valid(self):
        '''
        These are all formats that should be valid, thus return nothing when DEBUG is True.
        '''
        success_template_tests = (
            # one valid template
            (('col_two.html', 'two columns'),),

            # two valid templates
            (('col_two.html', 'two columns'),
             ('col_three.html', 'three columns'),),

            # three valid templates
            (('col_two.html', 'two columns'),
             ('col_three.html', 'three columns'),
             ('nav_playground.html', 'navigation examples'),),

            # three valid templates + inheritance
            (('col_two.html', 'two columns'),
             ('col_three.html', 'three columns'),
             ('nav_playground.html', 'navigation examples'),
            ),

            # same valid templates as above, ensuring we don't short circuit when inheritance
            # magic comes first.
            (('col_two.html', 'two columns'),
             ('col_three.html', 'three columns'),
             ('nav_playground.html', 'navigation examples'),),
        )
        for value_to_test in success_template_tests:
            with SettingsOverride(DEBUG=True, POSER_TEMPLATES=value_to_test):
                self.assertEqual(None, post_patch_check())
