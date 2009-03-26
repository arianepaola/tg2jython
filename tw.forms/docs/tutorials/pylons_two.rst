.. _pylons_tutorial_two:

Using tw.forms with Pylons. Part 2
==================================

.. currentmodule:: tw.forms.fields

Using fancy fields
------------------

This tutorial will show how we can enhance the form we created in
:ref:`pylons_tutorial_one` with some fancy fields which use javascript to
enhance the user's experience.

A little theory
^^^^^^^^^^^^^^^

ToscaWidgets tracks the javascript (and CSS) dependencies of every widget so
whenever they're displayed on a page the appropiate links are included. The
middleware intercepts those requests that ask for one of these static files and
automatically serves them.

It has two mechanisms to "inject" these resources:

* The "soon-to-be-deprecated" one which is copied from the way
  TurboGears' widgets injects them.
  This method involves a "master" or "base" template which is inherited
  by every template you want to display widgets on, a special container in
  which you pass widgets to the template from the controller and a wrapper
  around the ``render_response`` Pylons' function. This method is a **pain** to
  set up and forces widgets to be passed from the controller to the template
  blurring the separation beteween the view and controller layers.

* The "soon-to-become-official" one which is based on an idea that
  Ian Bicking expressed in his `blog`_.
  This method is the recommended approach for two important reasons:

  #. It's **much** easier to set up.
  #. It lets you import the widgets directly from your template, freeing
     your controller from view code hence offering a better separation
     between the MVC layers.

  .. note::
     
     This method used to use `lxml`_ to inject the tags into the html but it now
     uses regular expressions. These removes this troublesome `C`_ dependency
     completely.

In this tutorial I will only cover the second mechanism.

Enable resource injection in the middleware
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just set a flag when initializing it. Change the line where it's stacked in
middleware.py so it looks like:

.. code-block:: python

    app = make_middleware(app, {
        'toscawidgets.framework' : 'pylons',
        'toscawidgets.framework.default_view' : 'mako',
        'toscawidgets.middleware.inject_resources' : True,
        })

.. warning::

   Configuring the middleware like this to inject resources does not play well
   with cacheing done at Pylons' :func:`render` function.
   In this scenario it is best to inject resources manually by calling
   :func:`tw.api.inject_resources` on the HTML string before cacheing it.


Add your fancy fields to the form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ok, a plain textarea is not the coolest way to edit a blog post... lets use a
rich text editor! First install the egg::

    $ easy_install tw.tinymce

Now import it in your widgets module:

.. code-block:: python

    from tw.tinymce import TinyMCE

Finally edit the ``content`` field so it looks like this:

.. code-block:: python

    class PostForm(forms.ListForm):
        class fields(WidgetsList):
            # Other fields...
            content = TinyMCE()

You should now be able to point your browser to http://localhost:5000/tutorial/
an see a full-featured rich text editor!


Styling the form
----------------

Using CSS
^^^^^^^^^

Form widgets produce produce plenty of class and id HTML attributes which are
usually enought to customize the forms appearance. Some useful classes are:

   * fielderror
        This class is applied to the divs that display form errors. For example
        to make errors red colored and bold you would add to your page's CSS:

        .. code-block:: css
            
            .fielderror {
                color: red;
                font-weight: bold;
            }

   * fieldhelp
        This class is applied to the divs that display the fields'
        :attr:`FormField.help_text` attribute.
        For example, to make the fields' help messages smaller in
        size and lighter in coloryou would add to your page's CSS:
            
        .. code-block:: css

            .fieldhelp {
                color: #aaa;
                font-size: 0.7em;
            }

   * has_error
        This class is applied to the outermost HTML elements of every
        :class:`FormField` that has produced an error when
        validating.
        For example, to make the fields that have an error have a red
        background you would add to your page's CSS:
            
        .. code-block:: css

            input.has_error,
            select.has_error,
            textarea.has_error {
                background-color: red;
            }

   * required
        This class is applied to both the input field and its label when the
        field is a required field. Required fields are found automatically
        by simulating validation with an empty value.
        For example, to make required fields' labels be bolder you would add
        to your page's CSS:
            
        .. code-block:: css

            label.required {
                font-weight: bold;
            }

Some other classes are produced by specialized :class:`FormField` subclasses.
The best way to find out all available CSS classes is to use a tool like
`Firebug <http://getfirebug.com/>`_ to query each DOM element.

Customizing the template
^^^^^^^^^^^^^^^^^^^^^^^^

XXX: Write me


.. _lxml: http://codespeak.net/lxml/
.. _blog: http://blog.ianbicking.org/lxml-transformations.html
.. _C: http://en.wikipedia.org/wiki/C_(programming_language)
