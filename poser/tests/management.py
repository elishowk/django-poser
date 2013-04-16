# -*- coding: utf-8 -*-
from __future__ import with_statement
from StringIO import StringIO
from poser.test_utils.testcases import POSERTestCase
from poser.test_utils.util.context_managers import SettingsOverride
from poser.api import create_page
from poser.management.commands import poser
from poser.models.pagemodel import Page

APPHOOK = "SampleApp"

class ManagementTestCase(POSERTestCase):

    def test_list_apphooks(self):
        out = StringIO()
        apps = ["poser", "poser.test_utils.project.sampleapp"]
        with SettingsOverride(INSTALLED_APPS=apps):
            create_page('Hello Page', "nav_playground.html", apphook=APPHOOK)
            self.assertEqual(Page.objects.filter(application_urls=APPHOOK).count(), 1) 
            command = poser.Command()
            command.stdout = out
            command.handle("list", "apphooks", interactive=False)
            self.assertEqual(out.getvalue(), "SampleApp\n")
            
    def test_uninstall_apphooks_without_apphook(self):
        out = StringIO()
        command = poser.Command()
        command.stdout = out
        command.handle("uninstall", "apphooks", APPHOOK, interactive=False)
        self.assertEqual(out.getvalue(), "no 'SampleApp' apphooks found\n")

    def test_uninstall_apphooks_with_apphook(self):
        out = StringIO()
        apps = ["poser", "poser.test_utils.project.sampleapp"]
        with SettingsOverride(INSTALLED_APPS=apps):
            create_page('Hello Page', "nav_playground.html", apphook=APPHOOK)
            self.assertEqual(Page.objects.filter(application_urls=APPHOOK).count(), 1)
            command = poser.Command()
            command.stdout = out
            command.handle("uninstall", "apphooks", APPHOOK, interactive=False)
            self.assertEqual(out.getvalue(), "1 'SampleApp' apphooks uninstalled\n")
            self.assertEqual(Page.objects.filter(application_urls=APPHOOK).count(), 0)
