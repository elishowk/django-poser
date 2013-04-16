# -*- coding: utf-8 -*-
from poser.management.commands.subcommands.base import SubcommandsCommand
from poser.models.pagemodel import Page
from django.core.management.base import NoArgsCommand


class ListApphooksCommand(NoArgsCommand):
    
    help = 'Lists all apphooks in pages'
    def handle_noargs(self, **options):
        urls = Page.objects.filter(application_urls__gt='').values_list("application_urls", flat=True)
        for url in urls:
            self.stdout.write('%s\n' % url)
            
class ListCommand(SubcommandsCommand):
    help = 'List commands'
    subcommands = {
        'apphooks': ListApphooksCommand,
    }