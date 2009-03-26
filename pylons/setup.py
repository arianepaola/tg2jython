try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.9.7rc2'

setup(
    name="Pylons",
    version=version,
    description='Pylons Web Framework',
    long_description="""
Pylons
======

The Pylons web framework is aimed at making webapps and large programmatic
website development in Python easy. Several key points:

* A framework to make writing web applications in Python easy

* Utilizes a minimalist, component-based philosophy that makes it easy to
  expand on

* Harness existing knowledge about Python

Knowing Python makes Pylons easy
---------------------------------

Pylons makes it easy to expand on your knowledge of Python to master Pylons for
web development. Using a MVC style dispath, Python knowledge is used at various
levels:

* The Controller is just a basic Python class, called for each
  request. Customizing the response is as easy as overriding __call__ to make
  your webapp work how you want.

* Mako templating compiles directly to Python byte-code for speed and utilizes
  Python for template control rather than creating its own template syntax for
  "for, while, etc"

Current Status
---------------

Pylons %s described on this page is stable.

There is also an unstable `develoment version
<https://www.knowledgetap.com/hg/pylons-dev/archive/tip.tar.gz#egg=Pylons-dev>`_ of Pylons.

Download and Installation
-------------------------

Pylons can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

    > easy_install Pylons

Dependant packages are automatically installed from
the `Pylons download page <http://pylonshq.com/download/>`_ .


""" % version,
    keywords='web wsgi framework sqlalchemy formencode mako templates buffet',
    license='BSD',
    author='Ben Bangert, Philip Jenvey, James Gardner',
    author_email='ben@groovie.org, pjenvey@underboss.org',
    url='http://www.pylonshq.com/',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        "Routes>=1.9.2", "WebHelpers>=0.6.1", "Beaker>=1.0",
        "Paste>=1.7.1", "PasteDeploy>=1.3.2", "PasteScript>=1.6.3",
        "FormEncode>=1.0.1", "simplejson>=1.8.1", "decorator>=2.2.0",
        "nose>=0.10.3", "Mako>=0.2.2", "WebOb==dev,>=0.9.3dev-r7504", "WebError>=0.9",
        "Tempita>=0.2",
    ],
    dependency_links=[
        "http://www.pylonshq.com/download/0.9.7"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Framework :: Pylons",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    extras_require = {
        'pudge': ["docutils>=0.4", "elementtree>=1.2.6", "kid>=0.9",
                  "Pygments>=0.7", "pudge>=0.1.3",
                  "buildutils>=0.1.2"],
        'cheetah':["Cheetah>=1.0", "TurboCheetah>=0.9.5"],
        'myghty':["Myghty>=1.1"],
        'kid':["kid>=0.9", "TurboKid>=0.9.1"],
        'genshi':["Genshi>=0.3.6"],
        'full':[
            "docutils>=0.4", "elementtree>=1.2.6",
            "Pygments>=0.7", "pudge>=0.1.3",
            "buildutils>=0.1.2", "Cheetah>=1.0",
            "TurboCheetah>=0.9.5", "kid>=0.9", "TurboKid>=0.9.1",
            "TurboJson>=1.1.1", 'Genshi>=0.4.4',
        ],
    },
    entry_points="""
    [paste.paster_command]
    controller = pylons.commands:ControllerCommand
    restcontroller = pylons.commands:RestControllerCommand
    shell = pylons.commands:ShellCommand

    [paste.paster_create_template]
    pylons = pylons.util:PylonsTemplate
    pylons_minimal = pylons.util:MinimalPylonsTemplate

    [python.templating.engines]
    pylonsmyghty = pylons.templating:MyghtyTemplatePlugin [myghty]

    [nose.plugins]
    pylons = pylons.test:PylonsPlugin
    """,
)
