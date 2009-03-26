.. _pylons_tutorial_one:

Using tw.forms with Pylons. Part 1
==================================

Introduction
------------

tw.forms is a form generation library built using ToscaWidgets. Since it is the
most used Tosca "widget", tw.forms is commonly believed to *be* ToscaWidgets
(even I often use the terms interchangeably).

ToscaWidgets is a framework to package and
distribute chunks of html templates, javascript, css and the python code that
makes them tick. When properly configured, widgets built with ToscaWidgets can
be used in any python framework or application that can use WSGI middleware.

This tutorial will focus on its usage on `Pylons`_, however, the core concepts
apply equally to any python web framework. The only difference is how TW's
middleware is integrated and the detailed steps provided (file paths, etc...)

Scope
-----

This tutorial will cover:

 * How to configure ToscaWidgets in Pylons.
 * How to build a simple web form using simple fields.
 * How to add validators to the form's fields.
 * How to use fancy fields which require javascript.

Requirements
------------

This tutorial has been tested with Pylons 0.9.6.1 and Toscawidgets 0.8.5.
Any version later than those should work fine too.

Since `Mako`_ is the official template language used by `Pylons`_, this tutorial
will use Mako templates too. Any python templating engine that implements a
``python.templating.engine`` entry-point should be usable too. Both to create
custom widgets and to display them on. ToscaWidgets has been tested on Mako,
`Genshi`_, `Kid`_ and `Cheetah`_.

To make installation easier and better separate the controller layer from the
view layer, this tutorial will use lxml to inject resources (css and javascript
links) into the html page.

Installation
------------

Use ``easy_install`` to install tw.forms, this should pull ToscaWidgets and all
required dependencies too::
    
    $ easy_install tw.forms


Pylons >= 0.9.6.1 is assumed to be already instaled.

Configuring ToscaWidgets
------------------------

Bootstrap an empty Pylons project to follow the rest of the tutorial::

    paster create --template=pylons TWTutorial

Now you should edit ``twtutorial.config.middleware`` to stack TW's middleware.

First of all, at the beginning of the module, import TW's middleware and
Pylons' HostFramework object:

.. code-block:: python

   from tw.api import make_middleware

Now, after the line that says "CUSTOM MIDDLEWARE HERE" inside ``make_app()``, 
add:

.. code-block:: python

    app = make_middleware(app, {
        'toscawidgets.framework' : 'pylons',
        'toscawidgets.framework.default_view' : 'mako',
        'toscawidgets.middleware.inject_resources' : True,
        })

You should now be able to launch your app with
``paster serve --reload development.ini``, point your browser to
http://localhost:5000/ and see Pylons's default welcome page.

Building your first tw.forms form
---------------------------------

.. currentmodule:: tw.forms.fields

Create a file called ``widgets.py`` inside the ``twtutorial`` package and type
or paste the following code::

    from tw import forms
    from tw.api import WidgetsList

    forms.FormField.engine_name = "mako"

    class PostForm(forms.ListForm):
        class fields(WidgetsList):
            title = forms.TextField()
            author = forms.SingleSelectField(
                options = ["Peter", "Lucy"]
                )
            content = forms.TextArea()

    post_form = PostForm("post_form")

The above code should be, more or less, self-explanatory:

We create a :class:`ListForm` subclass (a form which renders its fields in an
unordered list) which has three fields:

* a :class:`TextField`, which is a, surprise, single-line text entry field
* a :class:`SingleSelectField`, which is a drop-down kind of field
* a :class:`TextArea`, which is a multi-line text entry field

Then we initialize the form class as a module level instance and give it a
*post_form* id. This id will be useful later when we apply CSS selectors or
attach javascript event handlers.

Notice that the form is instantiated at import time. This is how widgets are
usually instantiated and used (but not neccesarily so). There is no
thread-safety issues with the above code because widgets are **state-less**,
that is, once it's initial state is fixed when initialized, it's attributes are
**never** modified again. This does not mean we cannot modify how they're
rendered on every request. We can do it by overriding their *params* when
rendering them, more on this later.

One special detail worth mentioning: Notice the line where we modify the
:attr:`FormField.engine_name` of the :class:`FormField` class attribute?
Well, this is because tw.forms was initially built using Genshi templates so
`Genshi`_ remains the default template engine used.
Roger Demetrescu has kindly ported all tw.forms'
templates to Mako so, in order to avoid the Genshi dependency and obtain a
significant speed boost, you can change this class attribute to ``mako`` and
all widgets inside the tw.forms package will use their Mako templates.

Displaying the form
-------------------

To see the markup that the form produces when rendered we can do it directly
from the command-line, just import the ``widgets`` module we just created and
call the ``post_form`` instance::

    >>> from twtutorial.widgets import post_form
    >>> print post_form()


Produces:

.. code-block:: html

    <form id="post_form" action="" method="post" class="postform">
        <div>
        </div>
        <ul class="field_list">
            <li class="even">            
                <label id="post_form_title.label" for="post_form_title" class="fieldlabel required">Title</label>
                <input type="text" name="title" class="textfield required" id="post_form_title" value="" />
            </li>
            <li class="odd">            
                <label id="post_form_author.label" for="post_form_author" class="fieldlabel">Author</label>
                <select name="author" class="singleselectfield" id="post_form_author">
            <option value="Peter">Peter</option>
            <option value="Lucy">Lucy</option>
    </select>
            </li>
            <li class="even">            
                <label id="post_form_content.label" for="post_form_content" class="fieldlabel">Content</label>
                <textarea id="post_form_content" name="content" class="textarea" rows="25" cols="79"></textarea>
            </li>
            <li class="odd">            
                <input type="submit" class="submitbutton" id="post_form_submit" value="Submit" />
            </li>
        </ul>
    </form>


I hope the above hints at one of the benefits tw.forms provides over writting
forms using plain old HTML: Valid, accesible, easily maintainable markup with
just a little over 5 lines of code.

As you can see, the :class:`ListForm` generates an unordered list of fields and
their labels. For the vast majority of forms it will suffice to add a stylesheet
to customize the visual appeatance of the form. If more control over the
generated layout is needed, the template can be overriden so each field can
be precisely positioned. This will be covered in an upcoming tutorial.

Using the form in your application
----------------------------------

Lets create a new controller and a mako template to use the this form in our
application. First the controller::

    $ paster controller tutorial


Now edit ``twtutorial.controllers.tutorial`` so it looks like::

    import logging

    from twtutorial.lib.base import *

    log = logging.getLogger(__name__)

    class TutorialController(BaseController):

        def index(self):
            return render('/tutorial.mako')

And add a file called ``tutorial.mako`` inside the ``templates`` folder with
the following code:

.. code-block:: mako

    <%!
        from twtutorial.widgets import post_form
    %>

    <html>
        <head>
            <title>ToscaWidgets Tutorial</title>
        </head>
        <body>
            <h1>Welcome to the ToscaWidgets tutorial!</h1>
            ${post_form()}
        </body>
    </html>


You should now be able to point your browser to http://localhost:5000/tutorial
and see the form we just created.

Using the form to validate input
--------------------------------

What we have just covered doesn't provide much more value than what using
`Mako`_ functions or webhelpers to generate the fields markup would have
provided.

However, tw.forms integrates nicely with `FormEncode`_ (does **not** replace
it!) to have the objects which will validate our input near the fields they're
validating.

Edit the ``PostForm`` widget
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lets edit the form we created before and make it look like this::

    from tw.forms.validators import UnicodeString, Email
    # All other imports...

    class PostForm(forms.ListForm):
        class fields(WidgetsList):
            title = forms.TextField(
                validator = UnicodeString(not_empty=True)
                )
            email = forms.TextField(
                validator = Email(not_empty=True)
                )
            author = forms.SingleSelectField(
                options = ["Peter", "Lucy"]
                )
            content = forms.TextArea()

Notice that:

.. currentmodule:: tw.forms.validators

* We're importing the validators from the :mod:`tw.forms.validators` module.
  This 
  module includes all validators from FormEncode but overrides
  :mod:`UnicodeString` so it doesn't encode strings when converting from python.
  This is needed because Genshi and Mako need all strings to be unicode
  internally (or at least be ascii encodable). tw.forms fully supports unicode
  which should be no surprise since I speak Español and write with funny
  decorated characters :).

* We added an email field (which makes little sense in a blog post form) for the
  sake of showing off the :class:`Email` validator.

Edit the template
^^^^^^^^^^^^^^^^^

To pass an ``action`` parameter when displaying the form. Edit the template
so that the line where the form is displayed looks like:

.. code-block:: mako

    ${post_form(action=h.url_for(controller='tutorial', action='save'))}
    
This is the "params-overriding" I talked about a few lines ago...

Edit the controller
^^^^^^^^^^^^^^^^^^^

To implement the ``save`` method. Edit the controller to add a method that looks
like::

    @validate(form=post_form, error_handler="index")
    def save(self):
        response.headers['Content-Type'] = 'text/plain'
        try:
            return pformat(self.form_result)
        except AttributeError:
            return "You must POST to this method, dummy!"

Note that:

* The :meth:`validate` decorator being used is **not** the one provided
  by Pylons's but one provided by :mod:`tw.mods.pylonshf`
  (``from tw.mods.pylonshf import validate``).

* ``post_form`` is the form instance in the ``widgets`` module
  (``from twtutorial.widgets import post_form``).

* The ``error_handler`` parameter is the name of the method that should be
  called when validation fails. When a form is validated and validation fails
  the resulting ``formencode.api.Invalid`` exception is stored for the duration
  of the current request, along with the invalid input, so the form can be
  redisplayed with user-friendly error messages and previous input.

* ``pformat`` belongs in the ``pprint`` module of the standard library
  (``from pprint import pformat``).


Try it out!
^^^^^^^^^^^

You should now be able to point your browser to http://localhost:5000/tutorial
and see the form with the new ``email`` field. Fill the form with invalid input
and submit it. You should see the error messages beside the fields with your
previous input pre-filled so you don't have to type it again (your users will
love you!).

When you finally fill it right you should see the dict the :meth:`validate`
decorator leaves at ``self.form_result``. Try to put some accented characters at
the ``title`` field, you should see that the field value is decoded into a
useful unicode value that your application can handle internally.

.. _Mako: http://www.makotemplates.org/
.. _Genshi: http://genshi.edgewall.org/
.. _FormEncode: http://formencode.org/
.. _Pylons: http://pylonshq.com/
.. _Cheetah: http://www.cheetahtemplate.org/
.. _Kid: http://www.kid-templating.org/
