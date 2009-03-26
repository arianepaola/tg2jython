.. _core_module:

:mod:`tw.forms.core`
====================

.. automodule:: tw.forms.core
   
    :class:`InputWidget`
    --------------------

    This is the base class for all widgets that can submit input. It has the
    machinery to validate and coerce the received data.

      .. autoclass:: tw.forms.core.InputWidget
         :members: adjust_value, validate, safe_validate, prepare_dict, post_init, name, error_at_request, value_at_request


    :class:`InputWidgetRepeater`
    ----------------------------

    This is the base class to create repeated InputWidgets.

    .. autoclass:: tw.forms.core.InputWidgetRepeater
