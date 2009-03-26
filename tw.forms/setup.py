#!/usr/bin/env python2.4

"""Setuptools setup file"""

import sys, os
from setuptools import setup, find_packages

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required ATM")

execfile(os.path.join("tw", "forms", "release.py"))

setup(
    name=__PACKAGE_NAME__,
    version=__VERSION__,
    description="Web Widgets for building and validating forms. (former ToscaWidgetsForms)",
    #long_description = "",
    install_requires=[
        'ToscaWidgets >= 0.9.3',
        'FormEncode >= 1.0.1',
        ],
    extras_require = dict(
        mako = ['Mako'],
        genshi = ['Genshi >= 0.3.6'],
        ),
    url = "http://toscawidgets.org",
    download_url = "http://toscawidgets.org/download",
    author=__AUTHOR__,
    author_email=__EMAIL__,
    license=__LICENSE__,
    test_suite = 'tests',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['tw'],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [toscawidgets.widgets]
    widgets = tw.forms
    samples = tw.forms.samples
    """,
    dependency_links=[
        'http://toscawidgets.org/download/',
        ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
)
