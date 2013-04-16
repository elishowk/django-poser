from setuptools import setup, find_packages
import os
import poser


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    author="Elias Showk @ CommOnEcoute SAS",
    author_email="elias.showk@commonecoute.fr",
    name='django-poser',
    version=poser.__version__,
    description='A publication manager of REST resources',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    url='https://github.com/elishowk/django-poser',
    license='GNU Affero GPL v3',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.3.5,<1.5',
        'south>=0.7.2',
        'django-guardian',
    ],
    tests_require=[
        'Pillow==1.7.7',
        'Sphinx==1.1.3',
        'Jinja2==2.6',
        'Pygments==1.5',
    ],
    packages=find_packages(exclude = ["project", "project.*"]),
    include_package_data=True,
    zip_safe = False,
    test_suite = 'runtests.main',
)
