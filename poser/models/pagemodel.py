# -*- coding: utf-8 -*-
from poser.models.managers import PageManager
from poser.models.metaclasses import PageMetaClass
from poser.apphook_pool import apphook_pool
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import copy
import datetime
from poser.app_base import POSERApp
from guardian.shortcuts import assign
from poser.utils import urlutils, page as page_utils
from django.template.defaultfilters import slugify


class Page(models.Model):
    """
    Da page model
    """
    __metaclass__ = PageMetaClass

    created_by = models.ForeignKey(User, help_text=_("created by"), related_name='created_by', null=True, blank=True)
    changed_by = models.ForeignKey(User, help_text=_("changed by"), related_name='changed_by', null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    changed_date = models.DateTimeField(auto_now=True, editable=False)
    publication_date = models.DateTimeField(_("publication date"), null=True, blank=True, help_text=_('When the page should go live. Status must be "Published" for page to go live.'), db_index=True)
    publication_end_date = models.DateTimeField(_("publication end date"), null=True, blank=True, help_text=_('When to expire the page. Leave empty to never expire.'), db_index=True)
    published = models.BooleanField(_("is published"), blank=True)
    site = models.ForeignKey(Site, null=True, blank=True, help_text=_('The site the page is hosted'), verbose_name=_("site"))
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, db_index=True, unique=False, editable=False)
    path = models.CharField(_("Path"), max_length=255, db_index=True, null=True, blank=True, editable=False)
    application = models.CharField(_('application'), max_length=200, blank=True, null=True, db_index=True)
    meta_description = models.TextField(_("description"), max_length=255, blank=True, null=True)
    meta_keywords = models.CharField(_("keywords"), max_length=255, blank=True, null=True)
    redirect = models.CharField(_("redirect"), max_length=255, blank=True, null=True)
    # Managers
    objects = PageManager()

    class Meta:
        app_label = 'poser'
        permissions = (
            ('view_page', 'Can view page'),
            ('change_permissions_page', 'Can change permissions of page'),
            ('publish_page', 'Can publish page'),
            ('change_advanced_settings_page', 'Can change advanced settings of page'),
        )
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('site', 'title')
        app_label = 'poser'

    def __unicode__(self):
        title = self.get_title()
        if title is None:
            title = u""
        return u'%s' % (title,)

    def get_absolute_url(self):
        path = self.get_path()
        return urlutils.urljoin(reverse('pages-root'), path)

    def update_path(self):
        """
        Build path from parent page's path and slug
        """
        slug = u'%s' % self.slug
        self.path = u'%s' % slug

    def save(self, commit=True, **kwargs):
        """
        Args:
            commit: True if model should be really saved
        """
        if not self.created_by:
            from poser.utils.permissions import get_current_user
            user = get_current_user()
            if user:
                self.created_by = user
        if self.created_by:
            self.changed_by = self.created_by

        # set default slug:
        if not self.slug and not self.pk:
            self.slug = _generate_valid_slug(self.title)
            self.update_path()

        # validate and normalize application hook name
        if self.application:
            self.application = _verify_apphook(self.application)
        else:
            self.application = None

        # validate publication date
        if self.publication_date:
            assert isinstance(self.publication_date, datetime.date)

        # validate publication end date
        if self.publication_end_date:
            assert isinstance(self.publication_end_date, datetime.date)

        # validate site
        if not self.site:
            self.site = Site.objects.get_current()
        else:
            assert isinstance(self.site, Site)
        # if the page is published we set the publish date if not set yet.
        if self.publication_date is None and self.published:
            self.publication_date = datetime.datetime.now()

        if commit:
            super(Page, self).save(**kwargs)

        if self.created_by and isinstance(self.created_by, User):
            assign_user_to_page(self, self.created_by, grant_all=True)

    def publish(self):
        """
        Returns: True if page was successfully published.
        """
        if self.changed_by and not self.changed_by.has_perm("publish_page"):
            return False
        if self.created_by and not self.created_by.has_perm("publish_page"):
            return False
        # Publish can only be called on moderated and draft pages
        if self.published is True:
            return True

        if not self.pk:
            self.save()

        self.published = True
        self.save()

        # fire signal after publishing is done
        import poser.signals as poser_signals
        poser_signals.post_publish.send(sender=Page, instance=self)

        return True

    def copy_page(self, target, site,
                  copy_permissions=True,
                  public_copy=False):
        """
        copy a page
        Doesn't checks for add page permissions anymore, this is done in PageAdmin.
        """
        page_copy = None

        if public_copy:
            # create a copy of the draft page - existing code loops through pages so added it to a list
            page = copy.copy(self)
        else:
            page = self

        # create a copy of this page by setting pk = None (=new instance)
        page.old_pk = page.pk
        page.pk = None
        page.published = False
        page.site = site

        # override default page settings specific for public copy
        if public_copy:
            page.published = True
            page_copy = page    # create a copy used in the return
        else:
            # only need to save the page if it isn't public
            # since it is saved above otherwise
            page.save()
            page.slug = page_utils.get_available_slug(page)
        return page_copy   # return the page_copy or None

    def get_draft_object(self):
        return self

    def get_path(self):
        """
        get the path of the page
        """
        return self.path

    def get_slug(self):
        """
        get the slug of the page
        """
        return self.slug

    def get_redirect(self):
        """
        get redirect
        """
        return self.redirect

    def get_title(self):
        """
        get the title of the page
        """
        return self.title

    def get_application(self):
        """
        get application name
        """
        return self.application


    def get_meta_description(self):
        """
        get content for the description meta tag for the page
        """
        return self.meta_description

    def get_meta_keywords(self):
        """
        get content for the keywords meta tag for the page
        """
        return self.meta_keywords

    def get_application(self):
        """
        get application conf for application hook
        """
        return self.application

    def has_view_permission(self, request):
        #anonymous user
        if settings.POSER_PUBLIC_FOR == 'all':
            # anyonymous user, all pages have restriction
            return True
        if request.user.is_authenticated():
            return self.has_generic_permission(request, "view")
        else:
            return False

    def has_change_permission(self, request):
        if request.user.is_superuser:
            return True
        return self.has_generic_permission(request, "change")

    def has_delete_permission(self, request):
        if request.user.is_superuser:
            return True
        return self.has_generic_permission(request, "delete")

    def has_publish_permission(self, request):
        if request.user.is_superuser:
            return True
        return self.has_generic_permission(request, "publish")

    def has_advanced_settings_permission(self, request):
        if request.user.is_superuser:
            return True
        return self.has_generic_permission(request, "advanced_settings")

    def has_change_permissions_permission(self, request):
        """
        Has user ability to change permissions for current page?
        """
        if request.user.is_superuser:
            return True
        return self.has_generic_permission(request, "change_permissions")

    def has_add_permission(self, request):
        """
        Has user ability to add page under current page?
        """
        if request.user.is_superuser:
            return True
        return self.has_generic_permission(request, "add")

    def has_generic_permission(self, request, perm_type):
        """
        Return true if the current user has permission on the page.
        Return the string 'All' if the user has all rights.
        """
        opts = self._meta
        codename = '%s.%s_%s' % (opts.app_label, perm_type, opts.object_name.lower())
        att_name = "permission_%s_cache" % codename
        if not hasattr(self, "permission_user_cache") or not hasattr(self, att_name) \
                or request.user.pk != self.permission_user_cache.pk:
            from poser.utils.permissions import has_generic_permission
            self.permission_user_cache = request.user
            setattr(self, att_name, has_generic_permission(
                    self.id, request.user, codename))
            if getattr(self, att_name):
                self.permission_edit_cache = True
        return getattr(self, att_name)

    def reload(self):
        """
        Reload a page from the database
        """
        return Page.objects.get(pk=self.pk)


def assign_user_to_page(page, user, can_add=False, can_change=False,
                        can_delete=False, can_change_advanced_settings=False,
                        can_publish=False, can_change_permissions=False,
                        can_view=False, grant_all=False, global_permission=False):
    """
    Assigns given user to page, and gives him requested permissions.

    See docs/extending_poser/api_reference.rst for more info
    """
    if grant_all and not global_permission:
        # shortcut to grant all permissions
        return assign_user_to_page(page, user, True, True, True, True,
                                   True, True, True)

    data = {
        'add_page': can_add,
        'change_page': can_change,
        'delete_page': can_delete,
        'change_advanced_settings_page': can_change_advanced_settings,
        'publish_page': can_publish,
        'change_permissions_page': can_change_permissions,
        'view_page': can_view,
    }
    for perm in data.iterkeys():
        if data[perm] is False:
            continue
        assign(perm, user, page)


def _verify_apphook(apphook):
    """
    Verifies the apphook given is valid and returns the normalized form (name)
    """
    if hasattr(apphook, '__module__') and issubclass(apphook, POSERApp):
        apphook_pool.discover_apps()
        assert apphook in apphook_pool.apps.values()
        return apphook.__name__
    elif isinstance(apphook, basestring):
        apphook_pool.discover_apps()
        assert apphook in apphook_pool.apps
        return apphook
    else:
        raise TypeError("apphook must be string or POSERApp instance")


def _generate_valid_slug(source):
    """
    Generate a valid slug for a page from source
    Parent is passed so we can make sure the slug is unique for this level in
    the page tree.
    """
    qs = Page.objects.get_query_set()
    used = qs.values_list('slug', flat=True)
    baseslug = slugify(source)
    slug = baseslug
    i = 1
    while slug in used:
        slug = '%s-%s' % (baseslug, i)
        i += 1
    return slug
