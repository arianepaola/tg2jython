import cgi
import unicodedata

from mako.filters import xml_escape


__all__ = ["attrs", "content"]


def attrs(context, args=None, attrs=None):
    # Emulates Genshi's AttrsDirective (poorly)
    args = args or []
    if not isinstance(args, list):
        args = args.items()
    if attrs:
        args.extend(attrs.items())

    return u" ".join([u'%s="%s"' % (k,xml_escape(unicode(v)))
                     for k,v in args if v is not None])


def content(context, value):
    if value is None:
        return ""
    else:
        return cgi.escape(unicode(value))

def safe_str(context, value):
    """Converts value to its string representation, if unicode it makes it ascii
    safe by converting characters above 128 to their <128 equivalents."""
    if isinstance(value, unicode):
        return ''.join(unicodedata.normalize("NFD",c)[0] for c in value)
    else:
        return str(value)
