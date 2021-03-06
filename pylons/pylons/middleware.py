"""Pylons' WSGI middlewares"""
import logging
import os.path
import urllib
import warnings

from paste.deploy.converters import asbool
from paste.errordocument import StatusBasedForward
from paste.recursive import RecursiveMiddleware
from paste.urlparser import StaticURLParser
from weberror.evalexception import EvalException
from weberror.errormiddleware import ErrorMiddleware
from webob import Request
from webhelpers.html import literal

import pylons
import pylons.legacy
from pylons.error import template_error_formatters

__all__ = ['ErrorDocuments', 'ErrorHandler', 'StaticJavascripts',
           'error_document_template', 'error_mapper', 'footer_html',
           'head_html', 'media_path']

log = logging.getLogger(__name__)

media_path = os.path.join(os.path.dirname(__file__), 'media')

head_html = """\
<link rel="stylesheet" href="{{prefix}}/media/pylons/style/itraceback.css" \
type="text/css" media="screen" />"""

footer_html ="""\
<script src="{{prefix}}/media/pylons/javascripts/traceback.js"></script>
<script>
var TRACEBACK = {
    uri: "{{prefix}}",
    host: "%s",
    traceback: "/tracebacks"
}
</script>
<div id="service_widget">
<h2 class="assistance">Online Assistance</h2>
<div id="nv">
<ul id="supportnav">
    <li class="nav active"><a class="overview" href="#">Overview</a></li>
    <li class="nav"><a class="search" href="#">Search Mail Lists</a></li>
    <li class="nav"><a class="posttraceback" href="#">Post Traceback</a></li>
</ul>
</div>
<div class="clearfix">&nbsp;</div>
<div class="overviewtab">
<h3>Looking for help?</h3>

<p>Here are a few tips for troubleshooting if the above traceback isn't
helping out.</p>

<ol>
<li>Search the mail list</li>
<li>Post the traceback, and ask for help on IRC</li>
<li>Post a message to the mail list, referring to the posted traceback</li>

</div>
<div class="posttracebacktab">
<p><b>Note:</b> Clicking this button will post your traceback to the PylonsHQ website.
The traceback includes the module names, Python version, and lines of code that you
can see above. All tracebacks are posted anonymously unless you're logged into the
PylonsHQ website in this browser.</p>
<input type="button" href="#" class="submit_traceback" value="Send TraceBack to PylonsHQ" style="text-align: center;"/>
</div>

<div class="searchtab">
<p>The following mail lists will be searched:<br />
<input type="checkbox" name="lists" value="pylons" checked="checked" /> Pylons<br />
<input type="checkbox" name="lists" value="python" /> Python<br />
<input type="checkbox" name="lists" value="mako" /> Mako<br />
<input type="checkbox" name="lists" value="sqlalchemy" /> SQLAlchemy</p>
<p class="query">for: <input type="text" name="query" class="query" /></p>

<p><input type="submit" value="Search" /></p>
<div class="searchresults">

</div>
</div>

</div>
<div id="pylons_logo">\
<img src="{{prefix}}/media/pylons/img/pylons-tower120.png" /></div>
<div class="credits">Pylons version %s</div>"""

class StaticJavascripts(object):
    """Middleware for intercepting requests for WebHelpers' included 
    javascript files.
    
    Triggered when PATH_INFO begins with '/javascripts/'.
    
    """
    def __init__(self, **kwargs):
        from webhelpers.rails.asset_tag import javascript_path
        self.javascripts_app = \
            StaticURLParser(os.path.dirname(javascript_path), **kwargs)
        
    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO', '').startswith('/javascripts/'):
            log.debug("Handling Javascript URL (Starts with /javascripts/)")
            return self.javascripts_app(environ, start_response)
        else:
            return self.javascripts_app.not_found(environ, start_response)


report_libs = ['pylons', 'genshi', 'sqlalchemy']

def ErrorHandler(app, global_conf, **errorware):
    """ErrorHandler Toggle
    
    If debug is enabled, this function will return the app wrapped in
    the WebError ``EvalException`` middleware which displays
    interactive debugging sessions when a traceback occurs.
    
    Otherwise, the app will be wrapped in the WebError
    ``ErrorMiddleware``, and the ``errorware`` dict will be passed into
    it. The ``ErrorMiddleware`` handles sending an email to the address
    listed in the .ini file, under ``email_to``.
    
    """
    if 'error_template' in errorware:
        del errorware['error_template']
        warnings.warn(pylons.legacy.error_template_warning,
                      DeprecationWarning, 2)

    if asbool(global_conf.get('debug')):
        footer = footer_html % (pylons.config.get('traceback_host', 
                                                  'beta.pylonshq.com'),
                                pylons.__version__)
        py_media = dict(pylons=media_path)
        app = EvalException(app, global_conf, 
                            templating_formatters=template_error_formatters,
                            media_paths=py_media, head_html=head_html, 
                            footer_html=footer,
                            libraries=report_libs)
    else:
        app = ErrorMiddleware(app, global_conf, **errorware)
    return app


def error_mapper(code, message, environ, global_conf=None, **kw):
    """Legacy function used with ErrorDocuments to provide a mapping
    of error codes to handle"""
    if environ.get('pylons.error_call'):
        return
    else:
        environ['pylons.error_call'] = True
    
    if global_conf is None:
        global_conf = {}
    codes = [401, 403, 404]
    if not asbool(global_conf.get('debug')):
        codes.append(500)
    if code in codes:
        # StatusBasedForward expects a relative URL (no SCRIPT_NAME)
        url = '/error/document/?%s' % (urllib.urlencode({'message': message,
                                                         'code': code}))
        return url


class StatusCodeRedirect(object):
    """Internally redirects a request based on status code
    
    StatusCodeRedirect watches the response of the app it wraps. If the 
    response is an error code in the errors sequence passed the request
    will be re-run with the path URL set to the path passed in.
    
    This operation is non-recursive and the output of the second 
    request will be used no matter what it is.
    
    Should an application wish to bypass the error response (ie, to 
    purposely return a 401), set 
    ``environ['pylons.status_code_redirect'] = True`` in the application.
    
    """
    def __init__(self, app, errors=(400, 401, 403, 404), path='/error/document'):
        """Initialize the ErrorRedirect
        
        ``errors``
            A sequence (list, tuple) of error code integers that should
            be caught.
        ``path``
            The path to set for the next request down to the 
            application. 
        
        """
        self.app = app
        self.errors = errors
        self.error_path = path
    
    def __call__(self, environ, start_response):
        req = Request(environ)
        new_req = req.copy_get()
        resp = orig_resp = req.get_response(self.app, catch_exc_info=True)
        if resp.status_int in self.errors and \
           'pylons.status_code_redirect' not in environ and self.error_path:
            new_req.path_info = self.error_path
            new_req.environ['pylons.original_response'] = resp
            new_req.environ['pylons.original_request'] = req
            resp = new_req.get_response(self.app, catch_exc_info=True)
            resp.status = orig_resp.status
        return resp(environ, start_response)


def ErrorDocuments(app, global_conf=None, mapper=None, **kw):
    """Wraps the app in error docs using Paste RecursiveMiddleware and
    ErrorDocumentsMiddleware
    
    All the args are passed directly into the ErrorDocumentsMiddleware. If no
    mapper is given, a default error_mapper is passed in.
    """
    if global_conf is None:
        global_conf = {}
    if mapper is None:
        mapper = error_mapper
    return RecursiveMiddleware(StatusBasedForward(app, global_conf=global_conf,
                                                  mapper=mapper, **kw))


error_document_template = literal("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
 <title>Server Error %(code)s</title>
 
<style type="text/css">
body {
  font-family: Helvetica, sans-serif;
}

table {
  width: 100%%;
}

tr.header {
  background-color: #006;
  color: #fff;
}

tr.even {
  background-color: #ddd;
}

table.variables td {
  verticle-align: top;
  overflow: auto;
}

a.button {
  background-color: #ccc;
  border: 2px outset #aaa;
  color: #000;
  text-decoration: none;
}

a.button:hover {
  background-color: #ddd;
}

code.source {
  color: #006;
}

a.switch_source {
  color: #0990;
  text-decoration: none;
}

a.switch_source:hover {
  background-color: #ddd;
}

.source-highlight {
  background-color: #ff9;
}

</style>

<!-- CSS Imports -->
<link rel="stylesheet" href="%(prefix)s/error/style/orange.css" type="text/css" media="screen" />

<!-- Favorite Icons -->
<link rel="icon" href="%(prefix)s/error/img/icon-16.png" type="image/png" />

<style type="text/css">
        .red {
            color:#FF0000;
        }
        .bold {
            font-weight: bold;
        }
</style>

</head>

<body id="documentation">
<!-- We are only using a table to ensure old browsers see the message correctly -->

<noscript>
<div style="border-bottom: 1px solid #808080">
<div style="border-bottom: 1px solid #404040">
<table width="100%%" border="0" cellpadding="0" bgcolor="#FFFFE1"><tr><td valign="middle"><img src="%(prefix)s/error/img/warning.gif" alt="Warning" /></td><td>&nbsp;</td><td><span style="padding: 0px; margin: 0px; font-family: Tahoma, sans-serif; font-size: 11px">Warning, your browser does not support JavaScript so you will not be able to use the interactive debugging on this page.</span></td></tr></table>
</div>
</div>
</noscript>
    
    <!-- Top anchor -->
    <a name="top"></a>
    
    <!-- Logo -->
    <h1 id="logo"><a class="no-underline" href="http://www.pylonshq.com"><img class="no-border" src="%(prefix)s/error/img/logo.gif" alt="Pylons" title="Pylons"/></a></h1>
    <p class="invisible"><a href="#content">Skip to content</a></p>

    <!-- Main Content -->

    <div id="nav-bar">

        <!-- Section Navigation -->
        <h4 class="invisible">Section Links</h4>

            <ul id="navlist">
                <li class="active"><a href="#" accesskey="1" class="active">Error %(code)s</a></li>
            </ul>
    </div>
    <div id="main-content">
    
        <div class="hr"><hr class="hr" /></div> 

        <div class="content-padding">
            
            <div id="main_data">
                <div style="float: left; width: 100%%; padding-bottom: 20px;">
                <h1 class="first"><a name="content"></a>Error %(code)s</h1>
                </div>
                
                %(message)s
                
            </div>

        </div>
        
        
            <!-- Footer -->

        <div class="hr"><hr class="clear" /></div>
    </div>
    
    <div style=" background: #FFFF99; padding: 10px 10px 10px 6%%; clear: both;">
        The Pylons Team | 
        <a href="#top" accesskey="9" title="Return to the top of the navigation links">Top</a>
    </div>
</body>
</html>
""")
