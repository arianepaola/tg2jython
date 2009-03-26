.. _forms:

Forms
=====

These are widgets which are designed to hold :class:`FormField` instances. They
automatically create a :class:`SubmitButton` if none is provided.

:class:`Form`
-------------

The base class of all forms. This widget does not provide a useful template by
itself and should be overriden to provide custom layout.

.. autoclass:: tw.forms.fields.Form
.. widgetbrowser:: tw.forms.fields.Form
   :tabs: source, template

:class:`TableForm`
------------------

This form renders its fields in a two-column table.

.. autoclass:: tw.forms.fields.TableForm
.. widgetbrowser:: tw.forms.fields.TableForm
   :tabs: source, template

:class:`ListForm`
-----------------

This form renders its fields in an unordered list

.. autoclass:: tw.forms.fields.ListForm
.. widgetbrowser:: tw.forms.fields.ListForm
   :tabs: source, template

.. _form_example:

An example
----------

Here's :class:`ListForm` with some fields and a repeated :class:`FieldSet`.

.. widgetbrowser:: tw.forms.samples.AddUserForm
   :size: x-large
