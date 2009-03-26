.. _tg1_app_example:

TurboGears 1.x app example
==========================

An example of a ``controllers.py`` file to use a `form`_ from ``tw.forms`` to
validate input:

.. literalinclude:: ../../examples/tg1sample/tg1sample/controllers.py

To display the form in the template and pass it an ``action`` parameter to
instruct the web browser to send the data to the ``process_form`` controller
add this line::

   ${form(person, action='process_form')}

You can see full working TurboGears app  inside the ``examples/tg1sample``
directory of a development snapshot `tarball`_

.. _tarball: /hg/ToscaWidgets/archive/tip.tar.gz
.. _form: /documentation/tw.forms/tutorials/sample_form.html
