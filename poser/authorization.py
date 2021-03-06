from tastypie.authorization import DjangoAuthorization

class PerUserDjangoAuthorization(DjangoAuthorization):
    """
    Uses permission checking from ``django.contrib.auth`` to map
    ``POST / PUT / DELETE / PATCH`` to their equivalent Django auth
    permissions and users
    """
    def is_authorized(self, request, object=None):
        klass = self.resource_meta.object_class

        # If it doesn't look like a model, we can't check permissions.
        if not klass or not getattr(klass, '_meta', None):
            return True

        permission_map = {
            'POST': ['%s.add_%s'],
            'PUT': ['%s.change_%s'],
            'DELETE': ['%s.delete_%s'],
            'PATCH': ['%s.add_%s', '%s.change_%s', '%s.delete_%s'],
            'OPTIONS': ['%s.view_%s'],
            'HEAD': ['%s.view_%s'],
            'GET': ['%s.view_%s'],
        }
        permission_codes = []

        # If we don't recognize the HTTP method, we don't know what
        # permissions to check. Deny.
        if request.method not in permission_map:
            return False

        for perm in permission_map[request.method]:
            permission_codes.append(perm % (klass._meta.app_label, \
                                            klass._meta.module_name))

        # User must be logged in to check permissions.
        if not hasattr(request, 'user'):
            return False
        return request.user.has_perms(permission_codes, object)
