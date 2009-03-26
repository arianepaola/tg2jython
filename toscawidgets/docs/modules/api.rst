.. _api_module:

:mod:`tw.api`
=============

Public symbols from ToscaWidgets core are exported through this package. It is
best to import them from here to ensure portability if TW's core is refactored.

.. automodule:: tw.api
   
Core Widgets
-------------

These are the building blocks of widgets.

:class:`Widget`
+++++++++++++++

.. autoclass:: tw.api.Widget
   :members:

   .. autoattribute:: tw.api.Widget.id
   .. autoattribute:: tw.api.Widget.is_root
   .. autoattribute:: tw.api.Widget.root
   .. autoattribute:: tw.api.Widget.displays_on
   .. autoattribute:: tw.api.Widget.path
   .. autoattribute:: tw.api.Widget.key
   .. attribute:: params

      A set with all the params declared in all the widget's bases and
      itself.
      This set is computed by :class:`tw.core.meta.WidgetType` from the
      class attribute.

      .. doctest::

         >>> from tw.api import Widget
         >>> class SomeWidget(Widget):
         ...    params = ["a", "b"]
         ...
         >>> "a" in SomeWidget.params
         True
         
         All params from Widget are present in SomeWidget's set too.

         >>> "id" in SomeWidget.params
         True

   .. attribute:: javascript

       A list of :class:`tw.api.JSLink` or :class:`tw.api.JSSource` instances
       that the widget should register for injection in the page whenever it
       is displayed

   .. attribute:: css

       A list of :class:`tw.api.CSSLink` or :class:`tw.api.CSSSource` instances
       that the widget should register for injection in the page whenever it
       is displayed


:class:`WidgetRepeater`
+++++++++++++++++++++++

.. autoclass:: tw.api.WidgetRepeater


Static resources
----------------

Tosca widgets can bundle their static resources, such as Javascript code,
CSS and images in their EGG distributions.

All widgets being used in a page register their resources automatically so
:ref:`TW's middleware <middleware_module>` can inject them into the page.

.. note:: Resources can also be injected manually after the page has been
   rendered using :func:`inject_resources`

These static files can be served by TW's middleware while
developing or moved to a directory where a fast server can serve them in
production [1]_ 

Base Widgets and mixins
+++++++++++++++++++++++

:class:`Resource`
~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.Resource
   :members: inject

:class:`JSMixin`
~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.JSMixin

:class:`CSSMixin`
~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.CSSMixin

Links
+++++

The following widgets are used to inject links to static files in the html
of the page widgets are rendered.

:class:`Link`
~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.Link
.. widgetbrowser:: tw.api.Link
   :tabs: parameters

:class:`JSLink`
~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.JSLink 
.. widgetbrowser:: tw.api.JSLink
   :tabs: template, parameters

:class:`CSSLink`
~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.CSSLink
.. widgetbrowser:: tw.api.CSSLink
   :tabs: template, parameters

Sources
+++++++

The following widgets are used to inject CSS and JS into the html page
widgets are being rendered on.

.. note:: Injecting links to static files using :class:`Link` ind its
   subclasses is recommended over injecting
   CSS or JS source since the former can be cached by the browser and
   further optimized for deployment. Besides that, there are third party
   tools which can help with creating them which won't work if CSS and JS
   code is embedded in the python source code

:class:`Source`
~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.Source
.. widgetbrowser:: tw.api.Source
   :tabs: parameters

:class:`JSSource`
~~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.JSSource
.. widgetbrowser:: tw.api.JSSource
   :tabs: parameters, template

:class:`CSSSource`
~~~~~~~~~~~~~~~~~~
.. autoclass:: tw.api.CSSSource
.. widgetbrowser:: tw.api.CSSSource
   :tabs: parameters, template

Javascript interfacing utilities
--------------------------------

The following objects can help interfacing with the Javascript side of the
widget from the Python side.

:class:`js_function`
++++++++++++++++++++
.. autoclass:: tw.api.js_function
   :members:

:class:`js_callback`
++++++++++++++++++++
.. autoclass:: tw.api.js_callback
   :members:

:class:`js_symbol`
++++++++++++++++++++
.. autoclass:: tw.api.js_symbol
   :members:

:func:`encode`
++++++++++++++++++++
.. autofunction:: tw.api.encode

Other
-----

:class:`WidgetsList`
++++++++++++++++++++

This object is just syntax sugar to have a DSL-like way to declare a list
of widgets. Although it's subclasses appear to have attributes, there's some
metaclass magic behind the scenes which turns the class into a list factory.

.. autoclass:: tw.api.WidgetsList

:class:`WidgetBunch`
++++++++++++++++++++

This class is used internally by :class:`Widget` (in the ``children`` and
``c`` attribute) and is rarely used standalone anymore.

.. autoclass:: WidgetBunch
   :members:

:func:`make_middleware`
+++++++++++++++++++++++
.. autofunction:: make_middleware

:func:`inject_resources`
++++++++++++++++++++++++
.. autofunction:: inject_resources


.. rubric:: Footnotes

.. [1] See :ref:`deploy` for more information
