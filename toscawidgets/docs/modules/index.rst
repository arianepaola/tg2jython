.. _modules:

Public symbols from the ToscaWidgets distribution should be imported from
:mod:`tw.api`.

All ToscaWidgets widget eggs, such as `tw.forms`_, etc. graft their namespaces
in the :mod:`tw` namespace [1]_. For example, to import form widgtes from
:mod:`tw.forms` on would do::

    from tw.forms import TextField, PasswordField

Modules
=======


.. toctree::
   :maxdepth: 2
   
   api
   middleware
   resource_injector
   host_framework


.. rubric:: Footnotes

.. [1] This is accomplished using setuptools' `namespace packages <http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages>`_

.. _tw.forms: /documentation/tw.forms
