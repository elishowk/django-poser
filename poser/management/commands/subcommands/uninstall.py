# -*- coding: utf-8 -*-
from poser.management.commands.subcommands.base import SubcommandsCommand
from poser.models import Page
from django.core.management.base import LabelCommand


class UninstallApphooksCommand(LabelCommand):
    
    args = "APPHOK_NAME"
    label = 'apphook name (eg SampleApp)'
    help = 'Uninstalls (sets to null) specified apphooks for all pages'
    
    def handle_label(self, label, **options):
        queryset = Page.objects.filter(application_urls=label)
        number_of_apphooks = queryset.count()

        if number_of_apphooks > 0:
            if options.get('interactive'):
                confirm = raw_input("""
You have requested to remove %d %r apphooks.
Are you sure you want to do this?
Type 'yes' to continue, or 'no' to cancel: """ % (number_of_apphooks, label))
            else:
                confirm = 'yes'
            if confirm == 'yes':
                queryset.update(application_urls=None)
                self.stdout.write('%d %r apphooks uninstalled\n' % (number_of_apphooks, label))
        else:
            self.stdout.write('no %r apphooks found\n' % label)
            
class UninstallCommand(SubcommandsCommand):
    help = 'Uninstall commands'
    subcommands = {
        'apphooks': UninstallApphooksCommand,
    }