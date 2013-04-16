# -*- coding: utf-8 -*-
"""
Public REST API to create POSER contents.
"""
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from poser.models import Page
from poser.apphook_pool import apphook_pool
from poser.forms import UserForm
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.validation import FormValidation


class SiteResource(ModelResource):
    """
    A REST wrapper around Site model
    """
    class Meta:
        queryset = Site.objects.all()
        resource_name = "site"
        always_return_data = True
        authentication = Authentication()
        authorization = Authorization()


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        always_return_data = True
        excludes = ['password', 'is_active', 'is_staff', 'is_superuser']
        authentication = Authentication()
        authorization = Authorization()
        validation = FormValidation(form_class=UserForm)


class PageResource(ModelResource):
    """
    A REST wrapper around Page model
    """
    site = fields.ForeignKey(SiteResource, 'site')
    created_by = fields.ForeignKey(UserResource, 'created_by')
    changed_by = fields.ForeignKey(UserResource, 'changed_by')

    class Meta:
        queryset = Page.objects.all()
        resource_name = "page"
        authentication = Authentication()
        always_return_data = True
        authorization = Authorization()
        filtering = {
            'id': ALL,
            'created_by': ALL_WITH_RELATIONS
        }

    def dehydrate(self, bundle):
        """
        populates the bundle.data with the application model associated
        """
        if apphook_pool.get_apphooks():
            # There are apphooks in the pool. Let's see if there is one for the
            # current page
            # since we always have a page at this point, applications_page_check is
            # pointless
            # page = applications_page_check(request, page, slug)
            # Check for apphooks! This time for real!
            apphook_name = bundle.obj.get_application()
            if apphook_name:
                apphook = apphook_pool.get_apphook(apphook_name)
                mod = __import__(apphook.module, fromlist=[apphook.klass])
                klass = getattr(mod, apphook.klass)
                if klass:
                    resource = klass()
                    try:
                        obj = resource.obj_get(page__id=bundle.obj.id)
                        appbundle = resource.build_bundle(obj=obj,
                                                          request=bundle.request)
                        appbundle = resource.full_dehydrate(appbundle)
                        bundle.data['application'] = appbundle
                    except resource._meta.object_class.DoesNotExist:
                        pass
        return bundle

    #def hydrate(self, bundle):
    #    """
    #    populates the bundle.data with the application model associated
    #    """
        #if apphook_pool.get_apphooks():
        #    # There are apphooks in the pool. Let's see if there is one for the
        #    # current page
        #    # since we always have a page at this point, applications_page_check is
        #    # pointless
        #    # page = applications_page_check(request, page, slug)
        #    # Check for apphooks! This time for real!
        #    apphook_name = bundle.obj.get_application()
        #    if apphook_name:
        #        apphook = apphook_pool.get_apphook(apphook_name)
        #        mod = __import__(apphook.module, fromlist=[apphook.klass])
        #        klass = getattr(mod, apphook.klass)
        #        if klass:
        #            resource = klass()
        #            obj = resource.obj_get(page__id=bundle.obj.id)
        #            appbundle = resource.build_bundle(obj=obj,
        #                                              request=bundle.request)
        #            appbundle = resource.full_dehydrate(appbundle)
        #            bundle.data['application'] = appbundle
        #return bundle
