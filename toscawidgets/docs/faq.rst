.. _faq:

Frequently Asked Questions
==========================

General Questions
-----------------

Why use a Widget?  My js/css code is so site specific I can't see how
widgets could help.

  Widgets provide reuseablity to your js and css components. ToscaWidgets
  also allow you to share your widgets in an open community.  The
  ToscaWidgets package provides you with a paster template to help you
  get started quickly with your own widget library.

OK, why ToscaWidgets then, aren't TG Widgets the same?

  ToscaWidgets have a much more portable api, and can be used in any
  WSGI app.  This portability makes it possible to move your "view"
  related code between TG1, TG2, Pylons, CherryPy, even Grok.  There
  are also some api differences between TG widgets and ToscaWidgets.

  XXX: Thoroughly document these

  Lastly, TGWidgets are going to be phased out for TG2, so there will no
  TGWidget support in TG2. (maybe TG1.1 too?)

I have a great widget, how do I share it with the community?

  Register at toscawidgets.org, `create a new repository <http://toscawidgets.org/repositories/new>`_ and drop a line at the `mailing list`_  and tell us
  about it!

ToscaWidgets seems to be lacking in Documentation.  How can I validate
its use?  Is there a good level of support for this project?

  (Is this still a faq? :)
  There is currently a ground-roots effort from leading TG developers
  to get the Docs up to snuff.  It is our hope that this question will
  disappear from the FAQ by Q2 2008.  The fact is that there is a lot of
  complexity to capture about how TW works, and much of that information
  is stored as doc strings in the code.  If you check http://toscawidgets.org/
  you will see a reasonable amount of auto-created docs from those strings.
  Other ways you can learn more about TW is to dig into the source code,
  which is reasonably annotated.  It is recommended that you read up
  on Metaclasses in python first.  There is also a message board at
  `mailing list`_ where you can always
  ask a question.  The board is fairly active, and our developers have been
  trying to fill out the documentation after a question has been asked.
  In short, we are working on it.

.. _mailing list: http://groups.google.com/group/toscawidgets-discuss


TG1.0 Specifically
------------------

I get::

    TypeError: No object (name: ToscaWidgets per-request storage) has been registered for this thread

Try this::

   easy_install -U Toscawidgets

After, make sure ToscaWidgets is turned ON by adding / changing this
line in the dev.cfg/prod.cfg or app.cfg::

   toscawidgets.on = True


I get::

    ValueError: need more than 2 values to unpack

Just to make sure you have the latest version of Genshi, do this::

        $ easy_install -U genshi

After, make sure Genshi is set as the default view by adding / changing this
line in the dev.cfg/prod.cfg or app.cfg::

   tg.defaultview = 'genshi'


Compatibility Issues
--------------------

Grok
~~~~

If you are going to use ToscaWidgets in a Grok application, you can as
long as your Grok app is a WSGI app.  Grok has a way of doing this `here
<http://grok.zope.org/documentation/tutorial/installing-and-setting-up-grok-under-mod-wsgi/installing-and-configuring-a-grok-site-under>`_

Then, you need to modify your grok.ini to include the toscawidgets
middleware:

add::

  [filter:tosca]
  use=egg:toscawidgets#middleware
  default_view=genshi


modify::

  [pipeline:main]
  pipeline = egg:Paste#cgitb egg:Paste#httpexceptions suppressZopeErrorHandling tosca bbb
