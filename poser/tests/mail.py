# -*- coding: utf-8 -*-
from poser.test_utils.testcases import POSERTestCase
from poser.utils.mail import mail_page_user_change
from django.core import mail

from django.contrib.auth.models import User


class MailTestCase(POSERTestCase):
    def setUp(self):
        mail.outbox = [] # reset outbox

    def test_mail_user_change(self):
        user = User.objects.create_superuser("username", "username@django-poser.org", "username")
        mail_page_user_change(user)
        self.assertEqual(len(mail.outbox), 1)
