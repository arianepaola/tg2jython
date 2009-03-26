import threading
import logging
import os
import errno
import string
import heapq
import mimetypes
from operator import itemgetter
from itertools import izip, chain, imap

from pkg_resources import resource_filename, working_set, Requirement, \
                          resource_stream
import tw
from tw.core.base import Widget
from tw.core.util import Enum, OrderedSet, RequestLocalDescriptor

__all__ = [
    "Resource", "Link", "JSLink", "CSSLink", "Source", "JSSource", "CSSSource",
    "locations", "merge_resources", 
    "retrieve_resources", "JSFunctionCalls", "IECSSLink", "IECSSSource",
    "IEJSLink", "IEJSSource", "JSMixin", "CSSMixin"
    ]

log = logging.getLogger(__name__)


from webob import Request, Response

class ResourcesApp(object):
    def __init__(self, prefix='/resources', bufsize=4*1024):
        self._lock = threading.Lock()
        self._dirs = []
        self.prefix = prefix
        self.bufsize = bufsize

    def _is_registered(self, webdir, dirname):
        for old_wd, old_dn in self:
            if webdir == old_wd:
                if dirname != old_dn:
                    raise ValueError("%s is already regsitered for %s" %
                                     (webdir, old_dn))
                else:
                    return True
        return False
    
    def register(self, modname, filename):
        if isinstance(modname, Requirement):
            modname = os.path.basename(working_set.find(modname).location)

        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        parts = ['', modname] + filter(None, dirname.split('/'))
        webdir = '/'.join(parts)

        self._lock.acquire()
        try:
            if not self._is_registered(webdir, dirname):
                heapq.heappush(self._dirs, (len(webdir), (webdir, dirname)))
                log.debug("Regsitered %s at %s", dirname, webdir)
        finally:
            self._lock.release()
        url = '/'.join([self.prefix, webdir.strip('/'), basename])
        return webdir, dirname, url

    def get_prefixed(self):
        return tuple((self.prefix + k, v) for k,v in self)
    
    def __iter__(self):
        return imap(itemgetter(1), heapq.nlargest(len(self._dirs), self._dirs))

    def __call__(self, environ, start_response): 
        req = Request(environ)
        path_info = req.path_info
        resp = self.serve_file(req)
        resp = resp or Response(status="404 Not Found")
        return resp(environ, start_response)
             
    def serve_file(self, req):
        stream, ct, enc = self.get_stream_type_encoding(req.path_info)
        if stream:
            resp = Response(request=req, app_iter=stream, content_type=ct)
            if enc:
                resp.content_type_params['charset'] = enc
            expires = int(req.environ.get('toscawidgets.resources_expire', 0))
            resp.cache_expires(expires)
            return resp
        else:
            return Response(status="404 Not Found")

    def is_resource(self, path_info):
        for webdir, dirname in self:
            if path_info.startswith(webdir):
                return True
        return False

    def get_stream_type_encoding(self, path_info):
        if not self.is_resource(path_info):
            return None, None, None
        parts = filter(None, path_info.split('/'))
        modname, relative_path = parts[0], '/'.join(parts[1:])
        try:
            stream = resource_stream(modname, relative_path)
            ct, enc  = mimetypes.guess_type(os.path.basename(relative_path))
            stream = _FileIter(stream, self.bufsize)
        except IOError, e:
            # For some reason pkg_resources sometimes sets errno to 0
            # when resource can't be found
            if e.errno != 0 and e.errno != errno.ENOENT:
                raise
            stream, ct, enc = None, None, None
        return stream, ct, enc

        
class _FileIter(object):
    def __init__(self, fileobj, bufsize):
        self.fileobj = fileobj
        self.bufsize = bufsize

    def __iter__(self):
        return self

    def next(self):
        buf = self.fileobj.read(self.bufsize)
        if not buf:
            raise StopIteration
        return buf

    def close(self):
        self.fileobj.close()


registry = ResourcesApp()

#------------------------------------------------------------------------------
# Base class for all resources
#------------------------------------------------------------------------------

class Resource(Widget):
    """
    A resource for your widget, like a link to external JS/CSS or inline
    source to include at the page the widget is displayed.

    It has the following parameters:

    `location`
        Location on the page where the resource should be placed. Available
        locations can be queried at ``Resource.valid_locations``
    """

    valid_locations = Enum('head','headbottom', 'bodytop', 'bodybottom')
    location = valid_locations.head

    def add_for_location(self, location):
        return location == self.location

    def inject(self):
        """
        Push this resource into request-local so it is injected to the page
        """
        tw.framework.register_resources(self.retrieve_resources())

    def register_resources(self):
        # A Resource is registered by other widgets, not by itself.
        pass

locations = Resource.valid_locations

#------------------------------------------------------------------------------
# Utility Mixins
#------------------------------------------------------------------------------

class CSSMixin:
    params = ["media"]
    media = "all"
    
    def post_init(self, *args, **kw):
        self._resources.add(self)


class JSMixin:
    def post_init(self, *args, **kw):
        self._resources.add(self)

class IEMixin:
    params = ["version"]
    version = ''

    _trans_table = ( ('>=',  '>',  '<=',  '<'), ('gte ', 'gt ', 'lte ', 'lt '))

    def _extend_template(self, d):
        d.version = str(d.version)
        for i, s in enumerate(self._trans_table[0]):
            d.version = d.version.replace(s, self._trans_table[1][i])
        s = ('', ' ')[int(bool(d.version))]
        d.template = "<!--[if IE%s${version}]>%s<![endif]-->"%(s,self.template)
    

#------------------------------------------------------------------------------
# Links
#------------------------------------------------------------------------------


class Link(Resource):
    """
    A link to an external resource, like a a JS or CSS file stored in the
    filesystem.

    Widgets automatically use the framework to register the directory where the 
    resource is located so be careful that those directories contains no
    private data!
    """

    params = {
        'link': 'Use this to specify an external link. If provided this will '\
                'be used as-is as the resources URL. modname and filename '\
                'will be ignored.',
        'filename': "The relative path (from the module's or distribution's "\
                    "path) of the file the Link should link to.",
        'modname': "The module that contains the Widget declaration. "\
                   "If not given, it defaults to the name of the module where "\
                   "the Link is declared. Must be an existent module name. "\
                   "You can also pass a pkg_resources.Requirement instance to "\
                   "point to the root of an egg distribution."
        }
    _link = None
    filename = None
    modname = None

    def __init__(self, *args, **kw):
        super(Link, self).__init__(*args, **kw)
        if not self.is_external:
            modname = self.modname or self.__module__
            self.webdir, self.dirname, self.link = registry.register(
                modname, self.filename
                )
        else:
            self.link = kw.get('link')

    @property
    def is_external(self):
        return not bool(self.filename and self.modname)

    def _get_link(self):
        if self.is_external:
            return self._link
        return tw.framework.url(self._link or '')

    def _set_link(self, link):
        self._link = link

    link = property(_get_link, _set_link)

    def __hash__(self):
        return hash(self.link)

    def __eq__(self, other):
        return getattr(other, "link", None) == self.link



class CSSLink(Link,CSSMixin):
    """
    A link to an external CSS file.
    """
    template = """\
<link rel="stylesheet" type="text/css" href="$link" media="$media" />"""


class IECSSLink(CSSLink, IEMixin):
    def update_params(self, d):
        CSSLink.update_params(self, d)
        self._extend_template(d)


class JSLink(Link, JSMixin):
    template = """<script type="text/javascript" src="$link"></script>"""


class IEJSLink(JSLink, IEMixin):
    def update_params(self, d):
        JSLink.update_params(self, d)
        self._extend_template(d)

#------------------------------------------------------------------------------
# Raw source Resources
#------------------------------------------------------------------------------


class Source(Resource):
    """
    An inlined chunk of source code

    Examples::
        
        >>> class MySource(Source):
        ...     template = "$src"
        ...     src = "foo=$foo"
        ...     source_vars = ["foo"]
        ...     foo = "bar"
        ...
        >>> s = MySource()
        >>> s.render()
        u'foo=bar'

        >>> s = MySource(foo='zoo')
        >>> s.render()
        u'foo=zoo'

        >>> s.render(foo='foo')
        u'foo=foo'

        The whole source can also be overriden

        >>> s.render(src='foo')
        u'foo'
    """
    params = {
        'src': "A string with the source to include between the resource's "\
               "tags. Can also be a template for string.Template. Any "\
               "attribute listed at ``source_vars`` will be fetched from the "\
               "instance or from the kw args to ``display`` or ``render`` "\
               "into a dictionary to provide values to fill in."
        }
        

    def __new__(cls, *args, **kw):
        """Support positional params. (src)"""
        src = None
        parent = None
        if len(args) > 0:
            src = args[0]
        kw.setdefault('src', src or getattr(cls, 'src', None))
        if len(args) > 1:
            parent = args[1]
        return Resource.__new__(cls, None, parent, [], **kw) 

    def update_params(self,d):
        super(Source, self).update_params(d)
        src = d.get('src')
        if src:
        #    source_vars = dict(
        #        v for v in [(k, getattr(self,k,None)) for k in self.source_vars]
        #        )
        #    source_vars.update(
        #        v for v in d.iteritems() if v[0] in self.source_vars
        #        )
            d['src'] = string.Template(src).safe_substitute(**source_vars)


    def __hash__(self):
        return hash(self.src)

    def __eq__(self, other):
        return self.src == getattr(other, "src", None)




class CSSSource(Source, CSSMixin):
    """
    An inlined chunk of CSS source code.
    """
    template = """<style type="text/css" media="$media">$src</style>"""


class IECSSSource(CSSSource, IEMixin):
    def update_params(self, d):
        super(IECSSSource, self).update_params(d)
        self._extend_template(d)


class JSSource(Source, JSMixin):
    """
    An inlined chunk of JS source code.
    """
    template = """<script type="text/javascript">$src</script>"""

class IEJSSource(JSSource, IEMixin):
    def update_params(self, d):
        JSSource.update_params(self, d)
        self._extend_template(d)



class JSFunctionCalls(JSSource):
    params = ["function_calls"]
    function_calls = []
    
    def __init__(self, id=None, parent=None, children=[], **kw):
        super(JSFunctionCalls, self).__init__(id, parent, children, **kw)
        self.src = "\n%s\n" % "\n".join(map(str, self.function_calls))

    

class JSDynamicFunctionCalls(JSFunctionCalls):
    params = ["call_getter"]
    call_getter = lambda s, location: []

    def update_params(self,d):
        super(JSDynamicFunctionCalls,self).update_params(d)
        # Keep in mind self._calls_for_request has calls for *all* widgets
        d.src = "\n%s\n" % "\n".join(
            map(str, chain(self.call_getter(self.location), d.function_calls))
            )

    # Since our src is generated dynamically base hash and equality on id
    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)


# Utilities to retrieve resources


def merge_resources(to, from_):
    """
    In-place merge all resources from ``from_`` into ``to``. Resources
    from ``to_`` will come first in each resulting OrderedSet.
    """
    for k in locations:
        from_location = from_.get(k)
        if from_location:
            to.setdefault(k, OrderedSet()).add_all(from_location)
    return to
    
def retrieve_resources(obj):
    """Recursively retrieve resources from obj"""
    ret = {}
    if getattr(obj, 'retrieve_resources', None):
        ret = obj.retrieve_resources()
    elif getattr(obj, 'itervalues', None):
        ret = retrieve_resources(obj.itervalues())
    elif getattr(obj, '__iter__', None):
        ret = reduce(merge_resources, imap(retrieve_resources, iter(obj)), {})
    return ret

class DynamicCalls(object):
    _calls_for_request = RequestLocalDescriptor('_calls_for_request')
    def __init__(self):
        self.call_widgets = {}
        for l in locations:
            #XXX A circular-ref is probably created here with 'call_getter' but
            # since we're a module-level singleton we don't care much
            w = JSDynamicFunctionCalls('dynamic_js_calls_for_'+l, location=l,
                                       call_getter=self._get_calls_for_request)
            self.call_widgets[l] = w
    
    def reset(self):
        del self._calls_for_request

    def inject_call(self, call, location="bodybottom"):
        self._get_calls_for_request(location).append(call)
        self.call_widgets[location].inject()

    def _get_calls_for_request(self, location):
        try:
            self._calls_for_request
        except AttributeError:
            log.debug("Initializing calls for request")
            self._calls_for_request = dict((l,[]) for l in locations)
        return self._calls_for_request[location]

dynamic_js_calls = DynamicCalls()
