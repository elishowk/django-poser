# -*- coding: utf-8 -*-
class AppAlreadyRegistered(Exception):
    pass


AppAllreadyRegistered = AppAlreadyRegistered # backwards compatibility, will be dropped in 2.3


class NotImplemented(Exception):
    pass


class SubClassNeededError(Exception):
    pass


class MissingFormError(Exception):
    pass


class PermissionsException(Exception):
    """Base permission exception
    """


class NoPermissionsException(PermissionsException):
    """Can be fired when some violate action is performed on permission system. 
    """


class Deprecated(Exception): pass


class DontUsePageAttributeWarning(Warning): pass