from django.contrib import admin
from poser.models import Page


class PoserAdmin(admin.ModelAdmin):
    save_as = True
    list_filter = ('title',)
    search_fields = ('title',)

admin.site.register(Page, PoserAdmin)
