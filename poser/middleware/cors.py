#import re
#from django.utils.text import compress_string
#from django.utils.cache import patch_vary_headers
from django.conf import settings

from django import http

XS_SHARING_ALLOWED_ORIGINS = getattr(settings, 'XS_SHARING_ALLOWED_ORIGINS', ['*'])

XS_SHARING_ALLOWED_METHODS = getattr(settings, 'XS_SHARING_ALLOWED_METHODS', [
    'POST',
    'GET',
    'OPTIONS',
    'PUT',
    'DELETE'
])


class CorsHeaders(object):
    """ Allows cross-domain XHR """

    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
            if 'HTTP_ACCESS_CONTROL_REQUEST_HEADERS' in request.META:
                response['Access-Control-Allow-Headers'] =  request.META['HTTP_ACCESS_CONTROL_REQUEST_HEADERS']
            if 'HTTP_ORIGIN' in request.META:
                if request.META['HTTP_ORIGIN'] in XS_SHARING_ALLOWED_ORIGINS or '*' in XS_SHARING_ALLOWED_ORIGINS:
                    response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
            else:
                response['Access-Control-Allow-Origin'] = ",".join(XS_SHARING_ALLOWED_ORIGINS)
            return response

        return None

    def process_response(self, request, response):
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
        if 'HTTP_ACCESS_CONTROL_REQUEST_HEADERS' in request.META:
            response['Access-Control-Allow-Headers'] =  request.META['HTTP_ACCESS_CONTROL_REQUEST_HEADERS']
        if 'HTTP_ORIGIN' in request.META:
            if request.META['HTTP_ORIGIN'] in XS_SHARING_ALLOWED_ORIGINS or '*' in XS_SHARING_ALLOWED_ORIGINS:
                response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
        else:
            response['Access-Control-Allow-Origin'] = ",".join(XS_SHARING_ALLOWED_ORIGINS)

        return response
