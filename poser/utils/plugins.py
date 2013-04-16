# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site

SITE_VAR = "site__exact"

def current_site(request):
    if SITE_VAR in request.REQUEST:
        return Site.objects.get(pk=request.REQUEST[SITE_VAR])
    else:
        site_pk = request.session.get('poser_admin_site', None)
        if site_pk:
            try:
                return Site.objects.get(pk=site_pk)
            except Site.DoesNotExist:
                return None
        else:
            return Site.objects.get_current()
