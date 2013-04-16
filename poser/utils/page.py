# -*- coding: utf-8 -*-
from django.conf import settings
import re

APPEND_TO_SLUG = "-copy"
COPY_SLUG_REGEX = re.compile(r'^.*-copy(?:-(\d)*)?$')

def is_valid_page_slug(page, slug, site, path=None):
    """Validates given slug depending on settings.
    """
    # Exclude the page with the publisher_state == page.PUBLISHER_STATE_DELETE
    from poser.models.pagemodel import Page
    qs = Page.objects.filter(site=site)
    ## Check for slugs
    if qs.filter(slug=slug).count():
        return False
    ## Check for path
    if path and qs.filter(path=path).count():
        return False
    return True

def get_available_slug(page, new_slug=None):
    """Smart function generates slug for title if current title slug cannot be
    used. Appends APPEND_TO_SLUG to slug and checks it again.

    (Used in page copy function)

    Returns: slug
    """
    slug = new_slug or page.slug
    # We need the full path for the title to check for conflicting urls
    page.slug = slug
    page.update_path()
    path = page.path
    # This checks for conflicting slugs/overwrite_url, for both published and unpublished pages
    # This is a simpler check than in page_resolver.is_valid_url which
    # takes into account actualy page URL
    if not is_valid_page_slug(page, slug, page.site, path):
        # add nice copy attribute, first is -copy, then -copy-2, -copy-3, ....
        match = COPY_SLUG_REGEX.match(slug)
        if match:
            try:
                next = int(match.groups()[0]) + 1
                slug = "-".join(slug.split('-')[:-1]) + "-%d" % next
            except TypeError:
                slug = slug + "-2"

        else:
            slug = slug + APPEND_TO_SLUG
        return get_available_slug(page, slug)
    else:
        return slug


def check_title_slugs(page):
    """Checks page slugs for duplicity if required, used after page move/
    cut/paste.
    """
    old_slug = page.slug
    page.slug = get_available_slug(page)
    if page.slug != old_slug:
        page.save()
