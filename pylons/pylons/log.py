"""Logging related functionality

This logging Handler logs to ``environ['wsgi.errors']`` as designated
in :pep:`333`.

"""
import logging
import types

import pylons

__all__ = ['WSGIErrorsHandler']

class WSGIErrorsHandler(logging.Handler):
    """A handler class that writes logging records to
    environ['wsgi.errors'].

    This code is derived from CherryPy's 
    :class:`cherrypy._cplogging.WSGIErrorHandler`.
    
    """
    def __init__(self, cache=True, *args, **kwargs):
        """Handle initialization
        
        ``cache``
            Whether or not the wsgi.errors stream is cached (instead of
            looked up via pylons.request.environ for logged message)
        
        """
        logging.Handler.__init__(self, *args, **kwargs)
        self.cache = cache
        self.cached_stream = None

    def get_wsgierrors(self):
        """Return the wsgi.errors stream

        Raises a TypeError when outside of a web request
        (pylons.request is not setup)
        
        """
        if not self.cache:
            return pylons.request.environ.get('wsgi.errors')
        elif not self.cached_stream:
            self.cached_stream = pylons.request.environ.get('wsgi.errors')
            return self.cached_stream
        return self.cached_stream

    def flush(self):
        """Flushes the stream"""
        try:
            stream = self.get_wsgierrors()
        except TypeError:
            pass
        else:
            if stream:
                stream.flush()

    def emit(self, record):
        """Emit a record"""
        try:
            stream = self.get_wsgierrors()
        except TypeError:
            pass
        else:
            if not stream:
                return
            try:
                msg = self.format(record)
                fs = "%s\n"
                if not hasattr(types, "UnicodeType"): #if no unicode support...
                    stream.write(fs % msg)
                else:
                    try:
                        stream.write(fs % msg)
                    except UnicodeError:
                        stream.write(fs % msg.encode("UTF-8"))
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)
