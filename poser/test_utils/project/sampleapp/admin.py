from django.contrib import admin
from poser.test_utils.project.sampleapp.models import Picture


class PictureAdmin(admin.ModelAdmin):
    model = Picture

admin.site.register(Picture, PictureAdmin)
