"""
Also used in poser.tests.ApphooksTestCase
"""

from django.conf.urls.defaults import *
from .models import PictureResource
from tastypie.api import Api


poser_api = Api(api_name='sample_api')
poser_api.register(PictureResource())

urlpatterns = patterns('poser.test_utils.project.sampleapp.views',
    url(r'^$', 'sample_view', {'message': 'sample root page'}, name='sample-root'),
    (r'', include(poser_api.urls)),
    url(r'^settings/$', 'sample_view', kwargs={'message': 'sample settings page'}, name='sample-settings'),
    url(r'^account/$', 'sample_view', {'message': 'sample account page'}, name='sample-account'),
    url(r'^account/my_profile/$', 'sample_view', {'message': 'sample my profile page'}, name='sample-profile'),
    url(r'^notfound/$', 'notfound', name='notfound'),
    url(r'^extra_1/$', 'extra_view', {'message': 'test urlconf'}, name='extra_first'),
    url(r'^', include('poser.test_utils.project.sampleapp.urls_extra')),
)
