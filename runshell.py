#!/usr/bin/env python
from poser.test_utils.cli import configure
from poser.test_utils.tmpdir import temp_dir


def main():
    with temp_dir() as STATIC_ROOT:
        with temp_dir() as MEDIA_ROOT:
            configure(
                ROOT_URLCONF='poser.test_utils.project.urls',
                STATIC_ROOT=STATIC_ROOT,
                MEDIA_ROOT=MEDIA_ROOT,
                DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': 'posertestdb.sqlite',
                    }
                }
            )
            from django.core.management import call_command
            call_command('shell')

if __name__ == '__main__':
    main()
