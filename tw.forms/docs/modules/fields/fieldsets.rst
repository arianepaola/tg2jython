.. _fieldsets:

.. currentmodule:: tw.forms.fields

Fieldsets
=========

These widget containers are designed to hold fields to edit a related item
inline in their parent's form. When a form containing a fieldset is validated,
all the fields in the fieldset will appear in a nested dictionary inside the
forms dict (Fill and submit this :ref:`sample form <form_example>` to undersand
it better)

To create fieldsets for purely layout purposes it is best to create a custom
template and put the fieldset markup there.

:class:`FieldSet`
------------------

This is the base class of all fieldset widgets. It has a very basic template
which should be overriden.

.. autoclass:: tw.forms.fields.FieldSet
.. widgetbrowser:: tw.forms.fields.FieldSet
   :tabs: source, template

:class:`TableFieldSet`
----------------------

.. autoclass:: tw.forms.fields.TableFieldSet
.. widgetbrowser:: tw.forms.fields.TableFieldSet
   :tabs: source, template

:class:`ListFieldSet`
----------------------

.. autoclass:: tw.forms.fields.ListFieldSet
.. widgetbrowser:: tw.forms.fields.ListFieldSet
   :tabs: source, template
