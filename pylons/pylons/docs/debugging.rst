.. _debugging:

===========================
Troubleshooting & Debugging
===========================

.. _interactive_debugging:

Interactive debugging
---------------------

Things break, and when they do, quickly pinpointing what went wrong and why makes a huge difference. By default, Pylons uses a customized version of `Ian Bicking's <http://blog.ianbicking.org/>`_ EvalException middleware that also includes full Mako/Myghty Traceback information. 

See the Enabling Debugging section of the `Getting Started <Getting+Started>`_ guide to enable the interactive debugging. 

The Debugging Screen 
-------------------- 

The debugging screen has three tabs at the top: 

``Traceback`` 
Provides the raw exception trace with the interactive debugger 

``Extra Data`` 
Displays CGI, WSGI variables at the time of the exception, in addition to configuration information 

``Template`` 
Human friendly traceback for Mako or Myghty templates 

Since Mako and Myghty compile their templates to Python modules, it can be difficult to accurately figure out what line of the template resulted in the error. The `Template` tab provides the full Mako or Myghty traceback which contains accurate line numbers for your templates, and where the error originated from. If your exception was triggered before a template was rendered, no Template information will be available in this section. 

Example: Exploring the Traceback 
-------------------------------- 

Using the interactive debugger can also be useful to gain a deeper insight into objects present only during the web request like the ``session`` and ``request`` objects. 

To trigger an error so that we can explore what's happening just raise an exception inside an action you're curious about. In this example, we'll raise an error in the action that's used to display the page you're reading this on. Here's what the docs controller looks like: 

.. code-block:: python 

    class DocsController(BaseController): 
        def view(self, url): 
            if request.path_info.endswith('docs'): 
                redirect_to('/docs/') 
            return render('/docs/' + url) 

Since we want to explore the ``session`` and ``request``, we'll need to bind them first. Here's what our action now looks like with the binding and raising an exception: 

.. code-block:: python 

    def view(self, url): 
        raise "hi" 
        if request.path_info.endswith('docs'): 
            redirect_to('/docs/') 
        return render('/docs/' + url) 

Here's what exploring the Traceback from the above example looks like (Excerpt of the relevant portion): 

.. image:: _static/doctraceback.gif 

Email Options 
-------------

You can make all sorts of changes to how the debugging works. For example if you disable the ``debug`` variable in the config file Pylons will email you an error report instead of displaying it as long as you provide your email address at the top of the config file: 

.. code-block:: ini 

    error_email_from = you@example.com 

This is very useful for a production site. Emails are sent via SMTP so you need to specify a valid SMTP server too. 

Changing the Debugger Theme 
--------------------------- 

If you are using Pylons in a commercial company it is useful to be able to change the theme of the debugger so that if an error occurs, a page with your company logo appears. You might also decide to remove the Pylons logo if you use the debugger a lot so that there is more space to view the traceback. 

You can change the theme by creating a new template. For example, a very simple template might look like this: 

.. code-block:: python 

    my_error_template = ''' 
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
    <head> 
    <title>Server Error</title> 
    %(head)s 
    <body id="documentation"> 
    %(extra_data)s 
    %(template_data)s 
    %(traceback_data)s 
    </body> 
    </html> 
    ''' 

The values are automatically substituted by the error middleware. You can also add ``%(prefix)s`` which is replaced by the path to your application so you can include CSS files or images. For example if your application had a file called ``style.css`` in a directory called ``css`` within your ``public`` directory, you could add the following line to your template to ensure that the CSS file was always correctly found: 

.. code-block:: html 

    <link rel="stylesheet" href="%(prefix)s/css/style.css" type="text/css" media="screen" /> 

If you want to retain the ability to switch between the different error displays you need a slightly more complicated example: 

.. code-block:: python 

    my_error_template = ''' 
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
    <head> 
    <title>Server Error</title> 
    %(head)s 
    <body id="documentation" onload="switch_display('%(set_tab)s')"> 
    <ul id="navlist"> 
    <li id='traceback_data_tab' class="active"> 
    <a href="javascript:switch_display('traceback_data')" id='traceback_data_link'>Traceback</a> 
    </li> 
    <li id='extra_data_tab' class=""> 
    <a href="javascript:switch_display('extra_data')" id='extra_data_link'>Extra Data</a> 
    </li> 
    <li id='template_data_tab'> 
    <a href="javascript:switch_display('template_data')" id='template_data_link'>Template</a> 
    </li> 
    </ul> 
    <div id="extra_data" class="hidden-data"> 
    %(extra_data)s 
    </div> 
    <div id="template_data" class="hidden-data"> 
    %(template_data)s 
    </div> 
    <div id="traceback_data"> 
    %(traceback_data)s 
    </div> 
    </body> 
    </html> 
    ''' 

In this case when you click on a link the relevant tab is displayed. As long as you keep the same IDs and class names, you can specify your own styles and create a theme like the one used by Pylons by default. 

Now that you have a template you need to use it in your application. In ``config/middleware.py`` change the following lines: 

.. code-block:: python 

    # Error Handling 
    app = ErrorHandler(app, 
            global_conf, error_template=error_template, **config.errorware) 

to use your template: 

.. code-block:: python 

    my_error_template = ''' 
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"> 
        <head> 
            <title>Server Error</title> 
            %(head)s 
        <body id="documentation"> 
            %(extra_data)s 
            %(template_data)s 
            %(traceback_data)s 
        </body> 
    </html> 
    ''' 
    app = ErrorHandler(app, global_conf, 
            error_template=my_error_template, **config.errorware) 

Your interactive debugger will now be themed with the new template. 
 

Error Handling Options 
====================== 

A number of error handling options can be specified in the config file. These are described in the `Error Handler <interactive_debugger.txt>`_ documentation but the important point to remember is that debug should always be set to ``false`` in production environments otherwise if an error occurs the visitor will be presented with the developer's interactive traceback which they could use to execute malicious code.
