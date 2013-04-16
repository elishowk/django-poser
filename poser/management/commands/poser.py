# -*- coding: utf-8 -*-
from __future__ import absolute_import
from poser.management.commands.subcommands.base import SubcommandsCommand
from poser.management.commands.subcommands.list import ListCommand
from poser.management.commands.subcommands.uninstall import UninstallCommand
from django.core.management.base import BaseCommand
from optparse import make_option
    
    
class Command(SubcommandsCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
        help='Tells django-poser to NOT prompt the user for input of any kind. '),
    )
    
    args = '<subcommand>'

    command_name = 'poser'
    
    subcommands = {
        'uninstall': UninstallCommand,
        'list': ListCommand,
    }
    
    @property
    def help(self):
        lines = ['django POSER command line interface.', '', 'Available subcommands:']
        for subcommand in sorted(self.subcommands.keys()):
            lines.append('  %s' % subcommand)
        lines.append('')
        lines.append('Use `manage.py poser <subcommand> --help` for help about subcommands')
        return '\n'.join(lines)