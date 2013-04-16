# -*- coding: utf-8 -*-
from django.db.models.base import ModelBase
from poser.models.managers import PageManager


class PageMetaClass(ModelBase):
    def __new__(cls, name, bases, attrs):
        super_new = super(PageMetaClass, cls).__new__

        if 'objects' in attrs:
            if not isinstance(attrs['objects'], PageManager):
                raise ValueError, ("Model %s extends PageModel, " +
                                   "so its 'objects' manager must be " +
                                   "a subclass of models.managers.PageManager") % (name,)
        else:
            attrs['objects'] = PageManager()

        return super_new(cls, name, bases, attrs)
