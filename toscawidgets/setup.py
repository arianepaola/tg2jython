"""Setuptools setup file"""

import sys, os

from setuptools import setup

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required ATM")

execfile(os.path.join("tw", "release.py"))

def get_description(fname='README.txt'):
    # Adapted from PEAK-Rules' setup.py
    # Get our long description from the documentation
    f = file(fname)
    lines = []
    for line in f:
        if not line.strip():
            break     # skip to first blank line
    for line in f:
        if line.startswith('Documentation contents'):
            break     # read to "Documentation contents..."
        lines.append(line)
    f.close()
    return ''.join(lines)

PACKAGES = [
    'tw', 
    'tw.core',
    'tw.mods',
    ]

# Requirements to install buffet plugins and engines
_extra_cheetah = ["Cheetah>=1.0", "TurboCheetah>=0.9.5"]
_extra_genshi = ["Genshi >= 0.3.5"]
_extra_kid = ["kid>=0.9.5", "TurboKid>=0.9.9"]
_extra_mako = ["Mako >= 0.1.1"]

# Requierements to run all tests
_extra_tests = _extra_cheetah + _extra_genshi + _extra_kid + _extra_mako + ['BeautifulSoup', 'WebTest']

setup(
    name=__PACKAGE_NAME__,
    version=__VERSION__,
    description="Web widget creation toolkit based on TurboGears widgets",
    long_description = get_description(),
    install_requires=[
        'WebOb',
        'simplejson',
        ],
    extras_require = {
        'cheetah': _extra_cheetah,
        'kid': _extra_kid,
        'genshi': _extra_genshi,
        'mako': _extra_mako,
        'testing': _extra_tests,
        'build_docs': [
            "Sphinx", 
            "WidgetBrowser", 
            ],
        },
    url = "http://toscawidgets.org/",
    download_url = "http://toscawidgets.org/download/",
    dependency_links=[
        'http://toscawidgets.org/download/',
        ],
    author=__AUTHOR__,
    author_email=__EMAIL__,
    license=__LICENSE__,
    test_suite = 'tests',
    packages = PACKAGES,
    namespace_packages = ['tw', 'tw.mods'],
    include_package_data=True,
    exclude_package_data={"thirdparty" : ["*"]},
    entry_points="""
    [distutils.commands]
    archive_tw_resources = tw.core.command:archive_tw_resources

    [python.templating.engines]
    toscawidgets = tw.core.engine_plugin:ToscaWidgetsTemplatePlugin

    [toscawidgets.host_frameworks]
    wsgi = tw.mods.wsgi:WSGIHostFramework
    pylons = tw.mods.pylonshf:PylonsHostFramework
    turbogears = tw.mods.tg:Turbogears

    [toscawidgets.widgets]
    widgets = tw.api
    resources = tw.api

    [paste.paster_create_template]
    toscawidgets=tw.paste_template:ToscaWidgetsTemplate

    [turbogears.extensions]
    toscawidgets=tw.mods.tg

    [paste.filter_app_factory]
    middleware = tw.api:make_middleware
    """,
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
