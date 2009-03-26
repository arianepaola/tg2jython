"""Helpers for configuration files."""

class ConfigurationError(Exception):
    pass

def validate_config(config, validator, filename=None):
    """Validate an application's configuration.

    ``config`` 
        A dict-like object containing configuration values.

    ``validator``
        A FormEncode `Schema``.  A ``FancyValidator`` is also acceptable if it
        operates on a dict of values (not on a single value) and raises
        ``Invalid`` with a dict of error messages (not a single error message).

    ``filename``
        The configuration file's path if known.  Paste users should pass
        ``config.__file__`` here.

    This helper depends on Ian Bicking's FormEncode package.
    """
    from formencode import Invalid
    try:
        return validator.to_python(config)
    except Invalid, e:
        if filename:
            message = "configuration file '%s'" % filename
        else:
            message = "the application configuration"
        message += " has the following errors: "
        lines = [message]
        for key, error in sorted(e.error_dict.iteritems()):
            message = "    %s: %s" % (key, error)
            lines.append(message)
        message = "\n".join(lines)
        raise ConfigurationError(message)
        

### This is a lower-level alternative to the validation function above, and
### may produce more appropriate error messages.  In Pylons, these functions
### should be called by a fix_config() function called in load_environment()
### in environment.py

class NotGiven(object):
    pass

def require(config, key):
    if key not in config:
        raise KeyError("config variable '%s' is required" % key)

def require_int(config, key, default=NotGiven):
    want_conversion = True
    if key not in config:
        if default is NotGiven:
            raise KeyError("config variable '%s' is required" % key)
        value = default
        want_conversion = False  # Bypass in case default is None.
    if want_conversion:
        try:
            value = int(config[key])
        except ValueError:
            raise ValueError("config variable '%s' must be int" % key)
    config[key] = value
    return value

def require_bool(config, key, default=NotGiven):
    from paste.deploy.converters import asbool
    want_conversion = True
    if key not in config:
        if default is NotGiven:
            raise KeyError("config variable '%s' is required" % key)
        value = default
        want_conversion = False  # Bypass in case default is None.
    if want_conversion:
        try:
            value = asbool(config[key])
        except ValueError:
            tup = key, config[key]
            raise ValueError("config option '%s' is not true/false: %r" % tup)
    config[key] = value
    return value

def require_dir(config, key, create_if_missing=False):
    from unipath import FSPath as Path
    try:
        dir = config[key]
    except KeyError:
        msg = "config option '%s' missing"
        raise KeyError(msg % key)
    dir = Path(config[key])
    if not dir.exists():
        dir.mkdir(parents=True)
    if not dir.isdir():
        msg = ("directory '%s' is missing or not a directory "
               "(from config option '%s')")
        tup = dir, key
        raise OSError(msg % tup)
