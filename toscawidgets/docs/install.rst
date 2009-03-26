.. _install:

Installation
============

ToscaWidgets can be installed using ``easy_install`` from `setuptools`_.

Install a release
-----------------

To install the latest stable release type in a shell::

    $ easy_install ToscaWidgets

Install a development snapshot
------------------------------

To install the latest development snapshot request the ``dev`` version::

    $ easy_install ToscaWidgets==dev


Integrating with your framework
-------------------------------

To use ToscaWidgets needs to interface the framework in which the widgets will
be used in to serve static resources, inject CSS & JS links and to initialize
a per-request storage area. Pre 0.3 versions of ToscaWidgets were pretty
*bolier-platey* to integrate but since then the interface has been greatly
simplified to only require two lines of code in most situations.


.. _wsgi_integration:

Integration into a WSGI app
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integration into a WSGI app only requires to stack ToscaWidget's
:mod:`tw.core.middleware <middleware>`::
    
    from tw.api import make_middleware
    
    def application(environ, start_response):
        # Your WSGI application
        .....

    application = make_middleware(application, {
        'toscawidgets.framework.default_view': 'mako',
        'toscawidgets.middleware.inject_resources': True,
        })

Now this wrapped app can be fed to any WSGI compliant server.
XXX: Explain config dict sent to make_middleware

There's a full example in :ref:`wsgi_app_example`


Integration into a Turbogears 1.x app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To display Tosca widgets on a Turbogears 1.X app enable ToscaWidgets extension
in ``yourapp/config/app.cfg`` by adding the following line::

    toscawidgets.on = True 

There's a full example in :ref:`tg1_app_example`

Integration into a Turbogears 2.x app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ToscaWidgets already comes pre-configured when you quickstart a TG2 app.

Integration into a CherryPy 3 app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since CherryPy 3 can use WSGI middleware integration only differs in CherryPy's
API to pipeline several middleware pieces.

There's a full example in :ref:`cherrypy_app_example`

Integration into a Pylons app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pylons is fully WSGI compliant inside out. See :ref:`wsgi_integration`.

Integration into a web.py app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Web.py can use WSGI middleware so the same method can be used as for the rest
of the WSGI frameworks, only using web.py's API. There's a full example at
:ref:`webpy_app_example`.

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
