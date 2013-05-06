#!/usr/bin/env python
from setuptools import setup

from muttpy.aliases import DESC, VERSION

setup(
    name = 'muttpy',
    version = VERSION,
    packages = [
        'muttpy'
    ],
    url = 'http://nrocco.github.io/',
    author = 'Nico Di Rocco',
    author_email = 'dirocco.nico@gmail.com',
    description = DESC,
    include_package_data = True,
    install_requires = [
        'caldav==0.1.12',
        'lxml==3.1.0',
        'nose==1.2.1',
        'python-dateutil==1.1',
        'python-ldap==2.4.10',
        'vobject==0.8.1c'
    ],
    dependency_links = [
        'https://github.com/nrocco/ldapper/tarball/master#egg=ldapper-dev',
    ],
    entry_points = {
        'console_scripts': [
            'mutt-aliases = muttpy.aliases:main',
        ]
    },
    classifiers = [
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
