"""Helpers producing simple HTML tags

Most helpers have an ``\*\*attrs`` argument to specify additional HTML
attributes.  A trailing underscore in the name will be deleted; this is 
especially important for attributes that match Python keywords; e.g.,
``class_``.  Some helpers handle certain keywords specially; these are noted in
the helpers' docstrings.
"""

import datetime
import os
import re
import urllib
import urlparse

from webhelpers.html import escape, HTML, literal, url_escape

__all__ = [
           # Form tags
           "form", 
           "end_form", 
           "text", 
           "textarea", 
           "hidden", 
           "file",
           "password", 
           "text", 
           "checkbox", 
           "radio", 
           "submit",
           "select", 
           "ModelTags",
           # hyperlinks
           "link_to",
           "link_to_if",
           "link_to_unless",
           # Table tags
           "th_sortable",
           # Other non-form tags
           "ol",
           "ul",
           "image",
           # Head tags
           "auto_discovery_link",
           "javascript_link",
           "stylesheet_link",
           # Utility functions
           "convert_boolean_attrs",
           ]


def form(url, method="post", multipart=False, **attrs):
    """An open tag for a form that will submit to ``url``.

    You must close the form yourself by calling ``end_form()`` or outputting
    </form>.
    
    Options:

    ``multipart``
        If set to True, the enctype is set to "multipart/form-data".
        You must set it to true when uploading files, or the browser will
        submit the filename rather than the file.

    ``method``
        The method to use when submitting the form, usually either 
        "GET" or "POST". If "PUT", "DELETE", or another verb is used, a
        hidden input with name _method is added to simulate the verb
        over POST.
    
    Examples:

    >>> form("/submit")
    literal(u'<form action="/submit" method="post">')
    >>> form("/submit", method="get")
    literal(u'<form action="/submit" method="get">')
    >>> form("/submit", method="put")
    literal(u'<form action="/submit" method="post"><input name="_method" type="hidden" value="put" />')
    >>> form("/submit", "post", multipart=True) 
    literal(u'<form action="/submit" enctype="multipart/form-data" method="post">')
    """
    if multipart:
        attrs["enctype"] = "multipart/form-data"
    method_tag = literal("")
    if method.lower() in ['post', 'get']:
        attrs['method'] = method
    else:
        attrs['method'] = "post"
        method_tag = HTML.input(type="hidden", name="_method", value=method)
    attrs["action"] = url
    return HTML.form(method_tag, _closed=False, **attrs)


def end_form():
    """Output "</form>".
    
    Example::

        >>> end_form()
        literal(u'</form>')
    """
    return literal("</form>")


def text(name, value=None, **attrs):
    """Create a standard text field.
    
    ``value`` is a string, the content of the text field.
    
    Options:
    
    * ``disabled`` - If set to True, the user will not be able to use
        this input.
    * ``size`` - The number of visible characters that will fit in the
        input.
    * ``maxlength`` - The maximum number of characters that the browser
        will allow the user to enter.
    
    The remaining keyword args will be standard HTML attributes for the tag.
    
    """
    set_input_attrs(attrs, "text", name, value)
    convert_boolean_attrs(attrs, ["disabled"])
    return HTML.input(**attrs)


def hidden(name, value=None, **attrs):
    """Create a hidden field.
    """
    set_input_attrs(attrs, "hidden", name, value)
    return HTML.input(**attrs)


def file(name, value=None, **attrs):
    """Create a file upload field.
    
    If you are using file uploads then you will also need to set the 
    multipart option for the form.

    Example::

        >>> file('myfile')
        literal(u'<input name="myfile" type="file" />')
    
    """
    set_input_attrs(attrs, "file", name, value)
    return HTML.input(**attrs)


def password(name, value=None, **attrs):
    """Create a password field.
    
    Takes the same options as text_field.
    
    """
    set_input_attrs(attrs, "password", name, value)
    return HTML.input(**attrs)


def textarea(name, content="", **attrs):
    """Create a text input area.
    
    Example::
    
        >>> textarea("body", "", cols=25, rows=10)
        literal(u'<textarea cols="25" name="body" rows="10"></textarea>')
    
    """
    attrs["name"] = name
    return HTML.textarea(content, **attrs)


def checkbox(name, value="1", checked=False, **attrs):
    """Create a check box.

    Options:

    * ``checked`` - If true, the checkbox will be initially checked.
      This may be specified as a positional argument.

    * ``disabled`` - If true, checkbox will be grayed out.

    * ``readonly`` - If true, the user will not be able to modify the checkbox.

    Example::
    
        >>> checkbox("hi")
        literal(u'<input name="hi" type="checkbox" value="1" />')
    
    """
    set_input_attrs(attrs, "checkbox", name, value)
    attrs["type"] = "checkbox"
    attrs["name"] = name
    attrs["value"] = value
    if checked:
        attrs["checked"] = "checked"
    convert_boolean_attrs(attrs, ["disabled", "readonly"])
    return HTML.input(**attrs)

def _make_safe_id_component(idstring):
    """Make a string safe for including in an id attribute.
    
    The HTML spec says that id attributes 'must begin with 
    a letter ([A-Za-z]) and may be followed by any number 
    of letters, digits ([0-9]), hyphens ("-"), underscores 
    ("_"), colons (":"), and periods (".")'. These regexps
    are slightly over-zealous, in that they remove colons
    and periods unnecessarily.
    
    Whitespace is transformed into underscores, and then
    anything which is not a hyphen or a character that 
    matches \w (alphanumerics and underscore) is removed.
    
    """
    # Transform all whitespace to underscore
    idstring = re.sub(r'\s', "_", '%s' % idstring)
    # Remove everything that is not a hyphen or a member of \w
    idstring = re.sub(r'(?!-)\W', "", idstring).lower()
    return idstring

def radio(name, value, checked=False, **attrs):
    """Create a radio button.
    
    The id of the radio button will be set to the name + ' ' + value to 
    ensure its uniqueness.  An ``id`` keyword arg overrides this.
    
    """
    set_input_attrs(attrs, "radio", name, value)
    if checked:
        attrs["checked"] = "checked"
    if not "id" in attrs:
        attrs["id"] = '%s_%s' % (name, _make_safe_id_component(value))
    return HTML.input(**attrs)


def submit(name, value, **attrs):
    """Create a submit button with the text ``value`` as the caption."""
    set_input_attrs(attrs, "submit", name, value)
    return HTML.input(**attrs)


def select(name, selected_values, options, **attrs):
    """Create a dropdown selection box.

    * ``name`` -- the name of this control.

    * ``selected_values`` -- a string or list of strings or integers giving
      the value(s) that should be preselected.

    * ``options`` -- an iterable of ``(value, label)`` pairs.  The value is 
      what's returned to the application if this option is chosen; the label
      is what's shown in the form.  You can also pass an iterable of strings,
      in which case the labels will be identical to the values.

      CAUTION: this is the opposite order of the old rails helper 
      ``options_for_select``.  The order was changed because
      most real-life lists have the value first, including dicts of the form
      ``{value: label}``.  For those dicts you can simply pass ``D.items()``
      as this argument.

      HINT: You can sort options alphabetically by label via:
      ``sorted(my_options, key=lambda x: x[1])``

    * ``multiple`` -- if true, this control will allow multiple
       selections.

    Any other keyword args will become HTML attributes for the <select>.

    Examples (call, result)::
    
        >>> select("currency", "$", [["$", "Dollar"], ["DKK", "Kroner"]])
        literal(u'<select name="currency">\\n<option selected="selected" value="$">Dollar</option>\\n<option value="DKK">Kroner</option>\\n</select>')
        >>> select("cc", "MasterCard", [ "VISA", "MasterCard" ], id="cc", class_="blue")
        literal(u'<select class="blue" id="cc" name="cc">\\n<option value="VISA">VISA</option>\\n<option selected="selected" value="MasterCard">MasterCard</option>\\n</select>')
        >>> select("cc", ["VISA", "Discover"], [ "VISA", "MasterCard", "Discover" ])
        literal(u'<select name="cc">\\n<option selected="selected" value="VISA">VISA</option>\\n<option value="MasterCard">MasterCard</option>\\n<option selected="selected" value="Discover">Discover</option>\\n</select>')
        
    """
    attrs["name"] = name
    convert_boolean_attrs(attrs, ["multiple"])
    # Accept None as selected_values meaning that no option is selected
    if selected_values is None:
        selected_values = ('',)
    # Turn a single string or integer into a list
    elif isinstance(selected_values, (basestring, int)):
        selected_values = (selected_values,)
    opts = []
    # Cast integer values to strings
    selected_values = map(unicode, selected_values)
    for option in options:
        if isinstance(option, basestring):
            value = label = option
        elif isinstance(option, (int, long)):
            value = label = unicode(option)
        else:
            value, label = option[:2]
            value = unicode(value)
            if not isinstance(label, literal):
                label = unicode(label)
        if value in selected_values:
            opt = HTML.option(label, value=value, selected="selected")
        else:
            opt = HTML.option(label, value=value)
        opts.append(opt)
    opts_html = "\n".join(opts)
    opts_html = literal("\n%s\n" % opts_html)
    return HTML.select(opts_html, **attrs)


class ModelTags(object):
    """A nice way to build a form for a database record.
    
    ModelTags allows you to build a create/update form easily.  (This is the
    C and U in CRUD.)  The constructor takes a database record, which can be
    a SQLAlchemy mapped class, or any object with attributes or keys for the
    field values.  Its methods shadow the the form field helpers, but it
    automatically fills in the value attribute based on the current value in
    the record.  (It also knows about the 'checked' and 'selected' attributes
    for certain tags.)

    You can also use the same form  to input a new record.  Pass ``None`` or
    ``""`` instead of a record, and it will set all the current values to a
    default value, which is either the `default` keyword arg to the method, or
    `""` if not specified.

    (Hint: in Pylons you can put ``mt = ModelTags(c.record)`` in your template,
    and then if the record doesn't exist you can either set ``c.record = None``
    or not set it at all.  That's because nonexistent ``c`` attributes resolve
    to `""` unless you've set ``config["pylons.strict_c"] = True``. However,
    having a ``c`` attribute that's sometimes set and sometimes not is
    arguably bad programming style.)
    """

    undefined_values = set([None, ""])

    def __init__(self, record, use_keys=False, date_format="%m/%d/%Y", 
        id_format=None):
        """Create a ``ModelTags`` object.

        ``record`` is the database record to lookup values in.  It may be
        any object with attributes or keys, including a SQLAlchemy mapped
        instance.  It may also be ``None`` or ``""`` to indicate that a new
        record is being created.  (The class attribute ``undefined_values``
        tells which values indicate a new record.)

        If ``use_keys`` is true, values will be looked up by key.  If false
        (default), values will be looked up by attribute.

        ``date_format`` is a strftime-compatible string used by the ``.date``
        method.  The default is American format (MM/DD/YYYY), which is
        most often seen in text fields paired with popup calendars.
        European format (DD/MM/YYYY) is "%d/%m/%Y".  ISO format (YYYY-MM-DD)
        is "%Y-%m-%d".

        ``id_format`` is a formatting-operator format for the HTML 'id' attribute.
        It should contain one "%s" where the tag's name will be embedded.
        """
        self.record = record
        self.use_keys = use_keys
        self.date_format = date_format
        self.id_format = id_format
    
    def checkbox(self, name, **kw):
        """Build a checkbox field.
        
        The box will be initially checked if the value of the corresponding
        database field is true.

        The submitted form value will be "1" if the box was checked. If the
        box is unchecked, no value will be submitted. (This is a downside of
        the standard checkbox tag.)
        """
        self._update_id(name, kw)
        value = kw.pop("value", "1")
        checked = bool(self._get_value(name, kw))
        return checkbox(name, value, checked, **kw)

    def date(self, name, **kw):
        """Same as text but format a date value into a date string.

        The value can be a `datetime.date`, `datetime.datetime`, `None`,
        or `""`.  The former two are converted to a string using the
        date format passed to the constructor.  The latter two are converted
        to "".

        If there's no database record, consult keyword arg `default`. It it's
        the string "today", use todays's date. Otherwise it can be any of the
        values allowed above.  If no default is specified, the text field is
        initialized to "".

        Hint: you may wish to attach a Javascript calendar to the field.
        """
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        if isinstance(value, datetime.date):
            value = value.strftime(self.date_format)
        elif value == "today":
            value = datetime.date.today().strftime(self.date_format)
        else:
            value = ""
        return text(name, value, **kw)

    def file(self, name, **kw):
        """Build a file upload field.
        
        User agents may or may not respect the contents of the 'value' attribute."""
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return file(name, value, **kw)

    def hidden(self, name, **kw):
        """Build a hidden HTML field."""
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return hidden(name, value, **kw)

    def password(self, name, **kw):
        """Build a password field.
        
        This is the same as a text box but the value will not be shown on the
        screen as the user types.
        """
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return password(name, value, **kw)

    def radio(self, name, checked_value, **kw):
        """Build a radio button.

        The radio button will initially be selected if the database value 
        equals ``checked_value``.  On form submission the value will be 
        ``checked_value`` if the button was selected, or ``""`` otherwise.

        The control's 'id' attribute will be modified as follows:

        1. If not specified but an 'id_format' was given to the constructor,
           generate an ID based on the format.
        2. If an ID was passed in or was generated by step (1), append an
           underscore and the checked value.  Before appending the checked
           value, lowercase it, change any spaces to ``"_"``, and remove any
           non-alphanumeric characters except underscores and hyphens.
        3. If no ID was passed or generated by step (1), the radio button 
           will not have an 'id' attribute.

        """
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        if 'id' in kw:
            kw["id"] = '%s_%s' % (kw['id'], _make_safe_id_component(checked_value))
        checked = (value == checked_value)
        return radio(name, checked_value, checked, **kw)

    def select(self, name, options, **kw):
        """Build a dropdown select box or list box.

        See the ``select()`` function for the meaning of the arguments.
        """
        self._update_id(name, kw)
        selected_values = self._get_value(name, kw)
        return select(name, selected_values, options, **kw)

    def text(self, name, **kw):
        """Build a text box."""
        self._update_id(name, kw)
        value = self._get_value(name, kw)
        return text(name, value, **kw)

    def textarea(self, name, **kw):
        """Build a rectangular text area."""
        self._update_id(name, kw)
        content = self._get_value(name, kw)
        return textarea(name, content, **kw)

    # Private methods.
    def _get_value(self, name, kw):
        """Get the current value of a field from the database record.

        ``name``: The field to look up.

        ``kw``: The keyword args passed to the original method.  This is
        _not_ a "\*\*" argument!  It's a dict that will be modified in place!

        ``kw["default"]`` will be popped from the dict in all cases for
        possible use as a default value.  If the record doesn't exist, this
        default is returned, or ``""`` if no default was passed.
        """
        default = kw.pop("default", "")
        # This used to be ``self.record in self.undefined_values``, but this
        # fails if the record is a dict because dicts aren't hashable.
        for undefined_value in self.undefined_values:
            if self.record == undefined_value:
                return default
        if self.use_keys:
            return self.record[name]    # Raises KeyError.
        else:
            return getattr(self.record, name)   # Raises AttributeError.

    def _update_id(self, name, kw):
        """Apply the 'id' attribute algorithm.

        ``name``: The name of the HTML field.

        ``kw``: The keyword args passed to the original method.  This is
        _not_ a "\*\*" argument!  It's a dict that will be modified in place!

        If an ID format was specified but no 'id' keyword was passed, 
        set the 'id' attribute to a value generated from the format and name.
        Otherwise do nothing.
        """
        if self.id_format is not None and 'id' not in kw:
            kw['id'] = self.id_format % name
        
#### Hyperlink tags

def link_to(label, url='', **attrs):
    """Create a hyperlink with the given text pointing to the URL.
    
    If the label is ``None`` or empty, the URL will be used as the label.

    This function does not modify the URL in any way.  The label will be
    escaped if it contains HTML markup.  To prevent escaping, wrap the label
    in a ``webhelpers.html.literal()``.
    """
    attrs['href'] = url
    if label == '' or label is None:
        label = url
    return HTML.a(label, **attrs)


def link_to_if(condition, label, url='', **attrs):
    """Same as ``link_to`` but return just the label if the condition is false.
    
    This is useful in a menu when you don't want the current option to be a
    link.  The condition will be something like:
    ``actual_value != value_of_this_menu_item``.
    """
    if condition:
        return link_to(label, url, **attrs)
    else:
        return label

def link_to_unless(condition, label, url='', **attrs):
    """Same as ``link_to`` but return just the label if the condition is true.
    """
    if not condition:
        return link_to(label, url, **attrs)
    else:
        return label

#### Table tags
def th_sortable(current_order, column_order, label, url,
    class_if_sort_column="sort", class_if_not_sort_column=None, 
    link_attrs=None, name="th", **attrs):
    """<th> for a "click-to-sort-by" column.

    Convenience function for a sortable column.  If this is the current sort
    column, just display the label and set the cell's class to
    ``class_if_sort_column``.
    
    ``current_order`` is the table's current sort order.  ``column_order`` is
    the value pertaining to this column.  In other words, if the two are equal,
    the table is currently sorted by this column.

    If this is the sort column, display the label and set the <th>'s class to
    ``class_if_sort_column``.

    If this is not the sort column, display an <a> hyperlink based on
    ``label``, ``url``, and ``link_attrs`` (a dict), and set the <th>'s class
    to ``class_if_not_sort_column``.  
    
    ``url`` is the literal href= value for the link.  Pylons users would
    typically pass something like ``url=h.url_for("mypage", sort="date")``.

    ``**attrs`` are additional attributes for the <th> tag.

    If you prefer a <td> tag instead of <th>, pass ``name="td"``.

    To change the sort order via client-side Javascript, pass ``url=None`` and
    the appropriate Javascript attributes in ``link_attrs``.

    Examples:

    >>> sort = "name"
    >>> th_sortable(sort, "name", "Name", "?sort=name")
    literal(u'<th class="sort">Name</th>')
    >>> th_sortable(sort, "date", "Date", "?sort=date")
    literal(u'<th><a href="?sort=date">Date</a></th>')
    >>> th_sortable(sort, "date", "Date", None, link_attrs={"onclick": "myfunc()"})
    literal(u'<th><a onclick="myfunc()">Date</a></th>')
    """
    from webhelpers.html import HTML
    if current_order == column_order:
        content = label
        class_ = class_if_sort_column
    else:
        link_attrs = link_attrs or {}
        content = HTML.a(label, href=url, **link_attrs)
        class_ = class_if_not_sort_column
    return HTML.th(content, class_=class_, **attrs)



#### Other non-form tags

def ul(items, default=None, li_attrs=None, **attrs):
    R"""Return an unordered list with each item wrapped in <li>.

    ``items``
        list of strings.

    ``default``
        value returned _instead of the <ul>_ if there are no items in the list.
        If ``None``, return an empty <ul>.

    ``li_attrs``
        dict of attributes for the <li> tags.

    Examples:

    >>> ul(["foo", "bar"])
    literal(u'<ul>\n<li>foo</li>\n<li>bar</li>\n</ul>')
    >>> ul(["A", "B"], li_attrs={"class_": "myli"}, class_="mylist") 
    literal(u'<ul class="mylist">\n<li class="myli">A</li>\n<li class="myli">B</li>\n</ul>')
    >>> ul([])
    literal(u'<ul></ul>')
    >>> ul([], default="")
    ''
    >>> ul([], default=literal('<span class="no-data">No data</span>'))
    literal(u'<span class="no-data">No data</span>')
    >>> ul(["A"], default="NOTHING")
    literal(u'<ul>\n<li>A</li>\n</ul>')
    """
    li_attrs = li_attrs or {}
    return _list("ul", items, default, attrs, li_attrs)

def ol(items, default=literal(""), li_attrs=None, **attrs):
    R"""Return an ordered list with each item wrapped in <li>.

    ``items``
        list of strings.

    ``default``
        value returned _instead of the <ol>_ if there are no items in the list.
        If ``None``, return an empty <ol>.

    ``li_attrs``
        dict of attributes for the <li> tags.

    Examples:

    >>> ol(["foo", "bar"])
    literal(u'<ol>\n<li>foo</li>\n<li>bar</li>\n</ol>')
    >>> ol(["A", "B"], li_attrs={"class_": "myli"}, class_="mylist") 
    literal(u'<ol class="mylist">\n<li class="myli">A</li>\n<li class="myli">B</li>\n</ol>')
    >>> ol([])
    literal(u'')
    """
    li_attrs = li_attrs or {}
    return _list("ol", items, default, attrs, li_attrs)

def _list(tag, items, default, attrs, li_attrs):
    content = [HTML.li(x, **li_attrs) for x in items]
    if content:
        content = [""] + content + [""]
    elif default is not None:
        return default
    content = literal("\n").join(content)
    return getattr(HTML, tag)(content, **attrs)
    

def image(url, alt, width=None, height=None, **attrs):
    """Return an image tag for the specified ``source``.

    ``url``
        The URL of the image.  (This must be the exact URL desired.  A
        previous version of this helper added magic prefixes; this is
        no longer the case.)
    
    ``alt``
        The img's alt tag. Non-graphical browsers and screen readers will
        output this instead of the image.  If the image is pure decoration
        and uninteresting to non-graphical users, pass "".  To omit the
        alt tag completely, pass None.

    ``width``
        The width of the image, default is not included

    ``height``
        The height of the image, default is not included
        
    Examples::

        >>> image('/images/rss.png', 'rss syndication')
        literal(u'<img alt="rss syndication" src="/images/rss.png" />')

        >>> image('/images/xml.png', "")
        literal(u'<img alt="" src="/images/xml.png" />')

        >>> image("/images/icon.png", height=16, width=10, alt="Edit Entry")
        literal(u'<img alt="Edit Entry" height="16" src="/images/icon.png" width="10" />')

        >>> image("/icons/icon.gif", alt="Icon", width=16, height=16)
        literal(u'<img alt="Icon" height="16" src="/icons/icon.gif" width="16" />')

        >>> image("/icons/icon.gif", None, width=16)
        literal(u'<img alt="" src="/icons/icon.gif" width="16" />')
        
    """
    if not alt:
        alt = ""
    if width is not None:
        attrs['width'] = width
    if height is not None:
        attrs['height'] = height
    return HTML.img(src=url, alt=alt, **attrs)

#### Tags for the HTML head

def javascript_link(*urls, **attrs):
    """Return script include tags for the specified javascript URLs.
    
    ``urls`` should be the exact URLs desired.  A previous version of this
    helper added magic prefixes; this is no longer the case.

    Specify the keyword argument ``defer=True`` to enable the script 
    defer attribute.

    Examples::
    
        >>> print javascript_link('/javascripts/prototype.js', '/other-javascripts/util.js')
        <script src="/javascripts/prototype.js" type="text/javascript"></script>
        <script src="/other-javascripts/util.js" type="text/javascript"></script>

        >>> print javascript_link('/app.js', '/test/test.1.js')
        <script src="/app.js" type="text/javascript"></script>
        <script src="/test/test.1.js" type="text/javascript"></script>
        
    """
    convert_boolean_attrs(attrs, ["defer"])
    tags = []
    for url in urls:
        tag = HTML.script("", type="text/javascript", src=url, **attrs)
        tags.append(tag)
    return literal("\n").join(tags)


def stylesheet_link(*urls, **attrs):
    """Return CSS link tags for the specified stylesheet URLs.

    ``urls`` should be the exact URLs desired.  A previous version of this
    helper added magic prefixes; this is no longer the case.

    Examples::

        >>> stylesheet_link('/stylesheets/style.css')
        literal(u'<link href="/stylesheets/style.css" media="screen" rel="stylesheet" type="text/css" />')

        >>> stylesheet_link('/stylesheets/dir/file.css', media='all')
        literal(u'<link href="/stylesheets/dir/file.css" media="all" rel="stylesheet" type="text/css" />')

    """
    if "href" in attrs:
        raise TypeError("keyword arg 'href' not allowed")
    attrs.setdefault("rel", "stylesheet")
    attrs.setdefault("type", "text/css")
    attrs.setdefault("media", "screen")
    tags = []
    for url in urls:
        tag = HTML.link(href=url, **attrs)
        tags.append(tag)
    return literal('\n').join(tags)


def auto_discovery_link(url, feed_type="rss", **attrs):
    """Return a link tag allowing auto-detecting of RSS or ATOM feed.
    
    The auto-detection of feed for the current page is only for
    browsers and news readers that support it.

    ``url``
        The URL of the feed.  (This should be the exact URLs desired.  A
        previous version of this helper added magic prefixes; this is no longer
        the case.)

    ``feed_type``
        The type of feed. Specifying 'rss' or 'atom' automatically 
        translates to a type of 'application/rss+xml' or 
        'application/atom+xml', respectively. Otherwise the type is
        used as specified. Defaults to 'rss'.
        
    Examples::

        >>> auto_discovery_link('http://feed.com/feed.xml')
        literal(u'<link href="http://feed.com/feed.xml" rel="alternate" title="RSS" type="application/rss+xml" />')

        >>> auto_discovery_link('http://feed.com/feed.xml', feed_type='atom')
        literal(u'<link href="http://feed.com/feed.xml" rel="alternate" title="ATOM" type="application/atom+xml" />')

        >>> auto_discovery_link('app.rss', feed_type='atom', title='atom feed')
        literal(u'<link href="app.rss" rel="alternate" title="atom feed" type="application/atom+xml" />')

        >>> auto_discovery_link('/app.html', feed_type='text/html')
        literal(u'<link href="/app.html" rel="alternate" title="" type="text/html" />')
        
    """
    if "href" in attrs:
        raise TypeError("keyword arg 'href' is not allowed")
    if "type" in attrs:
        raise TypeError("keyword arg 'type' is not allowed")
    title = ""
    if feed_type.lower() in ('rss', 'atom'):
        title = feed_type.upper()
        feed_type = 'application/%s+xml' % feed_type.lower()
    attrs.setdefault("title", title)
    return HTML.link(rel="alternate", type=feed_type, href=url, **attrs)



########## INTERNAL FUNCTIONS ##########

def convert_boolean_attrs(attrs, bool_attrs):
    """Convert boolean values into proper HTML attributes.

    ``attrs`` is a dict of HTML attributes, which will be modified in
    place.

    ``bool_attrs`` is a list of attribute names.

    For every element in ``bool_attrs``, I look for a corresponding key in
    ``attrs``.  If its value is true, I change the value to match the key.
    For example, I convert ``selected=True`` into ``selected="selected"``.  If
    the value is false, I delete the key.
    
    """
    for a in bool_attrs:
        if attrs.has_key(a) and attrs[a]:
            attrs[a] = a
        elif attrs.has_key(a):
            del attrs[a]

def set_input_attrs(attrs, type, name, value):
    attrs["type"] = type
    attrs["name"] = name
    attrs["value"] = value


if __name__ == "__main__":
    import doctest
    doctest.testmod()
