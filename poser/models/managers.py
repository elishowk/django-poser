# -*- coding: utf-8 -*-
from poser.models.query import PageQuerySet
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q


class PageManager(models.Manager):
    """Use draft() and public() methods for accessing the corresponding
    instances.
    """

    def get_query_set(self):
        """Change standard model queryset to our own.
        """
        return PageQuerySet(self.model)

    # !IMPORTANT: following methods always return access to draft instances,
    # take care on what you do one them. use Page.objects.public() for accessing
    # the published page versions

    # Just some of the queryset methods are implemented here, access queryset
    # for more getting more supporting methods.

    # TODO: check which from following methods are really required to be on
    # manager, maybe some of them can be just accessible over queryset...?
    def get_title(self):
        """
        Gets the latest content for a particular page.
        """
        try:
            return self.title
        except self.model.DoesNotExist:
            pass
        return None

    def get_page_slug(self, slug, site=None):
        """
        Returns the latest slug for the given slug and checks if it's available
        on the current site.
        """
        if not site:
            site = Site.objects.get_current()
        try:
            pages = self.filter(
                slug=slug,
                site=site,
            ).select_related()  # 'page')
        except self.model.DoesNotExist:
            return None
        else:
            return pages


    def on_site(self, site=None):
        return self.get_query_set().on_site(site)

    def published(self, site=None):
        return self.get_query_set().published(site)

    def public(self):
        return self.get_query_set().filter(published=True)

    def drafts(self):
        return self.get_query_set().filter(published=False)

    def expired(self):
        return self.get_query_set().expired()

    def get_all_pages_with_application(self):
        """Returns all pages containing applications for all sites.
        """
        return self.get_query_set().filter(application_urls__gt='').distinct()

    def search(self, q, current_site_only=True):
        """Simple search function

        Plugins can define a 'search_fields' tuple similar to ModelAdmin classes
        """
        qs = self.get_query_set()

        if current_site_only:
            site = Site.objects.get_current()
            qs = qs.filter(site=site)

        qt = Q(title__icontains=q)

        qs = qs.filter(qt)
        return qs.distinct()


