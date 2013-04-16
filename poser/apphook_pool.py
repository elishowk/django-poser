# -*- coding: utf-8 -*-
from poser.exceptions import AppAlreadyRegistered
from poser.utils.django_load import load, iterload_objects
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class ApphookPool(object):
    def __init__(self):
        self.apps = {}
        self.discovered = False
        self.block_register = False

    def discover_apps(self):
        """
        Register PoserApp child classes declared in settings.POSER_APPHOOKS
        """
        if self.discovered:
            return
        #import all the modules
        if settings.POSER_APPHOOKS:
            self.block_register = True
            for cls in iterload_objects(settings.POSER_APPHOOKS):
                self.block_register = False
                self.register(cls)
                self.block_register = True
            self.block_register = False
        else:
            load('poser_app')
        self.discovered = True

    def clear(self):
        self.apps = {}
        self.discovered = False

    def register(self, app):
        if self.block_register:
            return
        from poser.app_base import POSERApp
        # validate the app
        if not issubclass(app, POSERApp):
            raise ImproperlyConfigured('POSER Apps must inherit '
                                       'poser.app_base.POSERApp, %r does not' % app)
        name = app.__name__
        if name in self.apps.keys():
            raise AppAlreadyRegistered("[%s] an poser app with this name is already registered" % name)
        self.apps[name] = app

    def get_apphooks(self):
        """
        returns an ordered set of (app name, app objects)
        """
        self.discover_apps()
        hooks = []
        for app_name in self.apps.keys():
            app = self.apps[app_name]
            hooks.append((app_name, app))
        hooks = sorted(hooks, key=lambda hook: hook[1])
        return hooks

    def get_apphook(self, app_name):
        """
        returns a PoserApp instance
        """
        self.discover_apps()
        try:
            return self.apps[app_name]
        except KeyError:
            pass
        raise ImproperlyConfigured('No registered apphook `%s` found.' % app_name)

# apphook_pool initialized on startup
apphook_pool = ApphookPool()
