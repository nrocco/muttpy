#!/usr/bin/env python
from setuptools import setup

import muttpy

setup(
    name = 'muttpy',
    version = muttpy.__version__,
    packages = [
        'muttpy'
    ],
    url = 'http://nrocco.github.io/',
    download_url = 'https://github.com/nrocco/muttpy',
    author = muttpy.__author__,
    author_email = 'dirocco.nico@gmail.com',
    description = 'A collection of command line scripts written '
                  'in Python for mutt (and davmail)',
    long_description = open('README.rst').read(),
    license = open('LICENSE').read(),
    include_package_data = True,
    install_requires = [
        'caldav==0.1.12',
        'ldapper==0.8.3',
        'pycli_tools==1.5',
        'python-dateutil==1.1',
        'python-ldap==2.4.10',
        'vobject==0.8.1c'
    ],
    entry_points = {
        'console_scripts': [
            'mutt-aliases = muttpy.aliases:main',
            'mutt-calendar = muttpy.calendar:main',
            'mutt-email = muttpy.emails:main',
        ]
    },
    classifiers = [
         'Operating System :: OS Independent',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
