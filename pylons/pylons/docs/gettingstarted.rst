.. _getting_started:

===============
Getting Started
===============

This section is intended to get Pylons up and running as fast as
possible and provide a quick overview of a project. Links are provided
throughout to encourage exploration of the various aspects of Pylons.


************
Requirements
************

* Python 2.3+ (Python 2.4+ highly recommended)

**********
Installing
**********

.. warning::
    
    These instructions require Python 2.4+. For installing with
    Python 2.3, see :ref:`python23_installation`.

To avoid conflicts with system-installed Python libraries, Pylons comes with a
boot-strap Python script that sets up a `virtual environment <http://pypi.python.org/pypi/virtualenv>`_. Pylons will then be
installed under the virtual environment.

.. admonition:: By The Way
    
    virtualenv is a useful tool to create isolated Python environments. In 
    addition to isolating packages from possible system conflicts, it makes
    it easy to install Python libraries using `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ without dumping lots
    of packages into the system-wide Python.
    
    The other great benefit is that no root access is required since all
    modules are kept under the desired directory. This makes it easy
    to setup a working Pylons install on shared hosting providers and other
    systems where system-wide access is unavailable.

1. Download the `go-pylons.py <http://www.pylonshq.com/download/0.9.7/go-pylons.py>`_ script.
2. Run the script and specify a directory for the virtual environment to be created under:
    
    .. code-block:: bash
        
        $ python go-pylons.py mydevenv

.. admonition:: Tip
    
    The two steps can be combined on unix systems with curl using the
    following short-cut:
    
    .. code-block:: bash
    
        $ curl http://pylonshq.com/download/0.9.7/go-pylons.py | python - mydevenv
    
    To isolate further from additional system-wide Python libraries, run
    with the no site packages option:
    
    .. code-block:: bash
    
        $ python go-pylons.py --no-site-packages mydevenv

This will leave a functional virtualenv and Pylons installation.
Activate the virtual environment (scripts may also be run by specifying the
full path to the mydevenv/bin dir):

.. code-block:: bash

    $ source mydevenv/bin/activate

Or on Window to activate:

.. code-block:: text
    
    > mydevenv\bin\activate.bat


Working Directly From the Source Code 
=====================================

`Mercurial <http://www.selenic.com/mercurial/wiki/>`_ must be installed to retrieve the latest development source for Pylons. `Mercurial packages <http://www.selenic.com/mercurial/wiki/index.cgi/BinaryPackages>`_ are also available for Windows, MacOSX, and other OS's. 

Check out the latest code: 

.. code-block:: bash 

    $ hg clone https://www.knowledgetap.com/hg/pylons-dev Pylons 

To tell setuptools to use the version in the ``Pylons`` directory: 

.. code-block:: bash 

    $ cd Pylons 
    $ python setup.py develop 

The active version of Pylons is now the copy in this directory, and changes made there will be reflected for Pylons apps running.


*************************
Creating a Pylons Project
*************************

Create a new project named ``helloworld`` with the following command:

.. code-block:: bash

    $ paster create -t pylons helloworld

.. note:: 
    
    Windows users must configure their ``PATH`` as described in :ref:`windows_notes`, otherwise they must specify the full path name to the ``paster`` command (including the virtual environment bin dir).

Running this will prompt for two choices, whether or not to include :term:`SQLAlchemy` support, and which template language to use. Hit enter both times to accept the defaults (no :term:`SQLAlchemy`, with Mako templating). 

The created directory structure with links to more information:

- helloworld
    - MANIFEST.in
    - README.txt
    - development.ini - :ref:`run-config`
    - docs
    - ez_setup.py
    - helloworld
        - __init__.py
        - config
            - environment.py - :ref:`environment-config`
            - middleware.py - :ref:`middleware-config`
            - routing.py - :ref:`url-config`
        - controllers - :ref:`controllers`
        - lib
            - app_globals.py - :term:`app_globals`
            - base.py
            - helpers.py - :ref:`helpers`
        - model - :ref:`models`
        - public
        - templates - :ref:`templates`
        - tests - :ref:`testing`
        - websetup.py - :ref:`run-config`
    - helloworld.egg-info
    - setup.cfg
    - setup.py - :ref:`setup-config`
    - test.ini


***********************
Running the application
***********************

Run the web application:

.. code-block:: bash

    $ cd helloworld
    $ paster serve --reload development.ini
    
The command loads the project's server configuration file in :file:`development.ini` and serves the Pylons application.

.. note::
    
    The ``--reload`` option ensures that the server is automatically reloaded
    if changes are made to Python files or the :file:`development.ini` 
    config file. This is very useful during development. To stop the server
    press :command:`Ctrl+c` or the platform's equivalent.

Visiting http://127.0.0.1:5000/ when the server is running will show the welcome page.


***********
Hello World
***********

To create the basic hello world application, first create a
:term:`controller` in the project to handle requests:

.. code-block:: bash

    $ paster controller hello

Open the :file:`helloworld/controllers/hello.py` module that was created.
The default controller will return just the string 'Hello World':

.. code-block:: python

    import logging

    from pylons import request, response, session
    from pylons import tmpl_context as c
    from pylons.controllers.util import abort, redirect_to, url_for

    from helloworld.lib.base import BaseController, render
    # import helloworld.model as model

    log = logging.getLogger(__name__)
    
    class HelloController(BaseController):

        def index(self):
            # Return a rendered template
            #   return render('/template.mako')
            # or, Return a response
            return 'Hello World'

At the top are some imports of common objects that are frequently used
in controllers.

Navigate to http://127.0.0.1:5000/hello/index where there should be a short text string saying "Hello World" (start up the app if needed):

.. image:: _static/helloworld.png

.. admonition:: How'd that get to /hello/index?
    
    :ref:`url-config` explains how URL's get mapped to controllers and
    their methods.

Add a template to render some of the information that's in the :term:`environ`.

First, create a :file:`hello.mako` file in the :file:`templates`
directory with the following contents:

.. code-block:: mako

    Hello World, the environ variable looks like: <br />
    
    ${request.environ}

The :term:`request` variable in templates is used to get information about the current request.`template globals <modules/templating.html#template-globals>`_ lists all the variables Pylons makes available for use in templates.

Next, update the :file:`controllers/hello.py` module so that the
index method is as follows:

.. code-block:: python

    class HelloController(BaseController):

        def index(self):
            return render('/hello.mako')

Refreshing the page in the browser will now look similar to this:

.. image:: _static/hellotemplate.png