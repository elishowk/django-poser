# -*- coding: utf-8 -*-
from datetime import datetime
from django.db.models import Q
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet

class PageQuerySet(QuerySet):
    def on_site(self, site=None):
        if not site:
            try:
                site = Site.objects.get_current()
            except Site.DoesNotExist:
                site = None
        return self.filter(site=site)

    def published(self, site=None):
        pub = self.on_site(site).filter(published=True)

        pub = pub.filter(
            Q(publication_date__lt=datetime.now()) |
            Q(publication_date__isnull=True)
        )

        pub = pub.filter(
            Q(publication_end_date__gte=datetime.now()) |
            Q(publication_end_date__isnull=True)
        )

        return pub

    def expired(self):
        return self.on_site().filter(
            publication_end_date__lte=datetime.now())

    def get_all_pages_with_application(self):
        """Returns all pages containing applications for all sites.

        """
        return self.published().filter(title_set__application_urls__gt='').distinct()
