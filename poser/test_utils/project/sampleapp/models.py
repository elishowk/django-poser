from django.db import models
from tastypie.resources import ModelResource
from poser.models import Page


class Picture(models.Model):
    image = models.ImageField(upload_to="sampleapp_pictures")
    page = models.ForeignKey(Page)


class PictureResource(ModelResource):
    class Meta:
        queryset = Picture.objects.all()
        resource_name = 'picture'
        always_return_data = True
