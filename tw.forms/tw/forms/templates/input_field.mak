<%namespace name="tw" module="tw.core.mako_util"/>\
<input ${tw.attrs(
    [('type', context.get('type')),
     ('name', name),
     ('class', css_class),
     ('id', context.get('id')),
     ('value', value)],
    attrs=attrs
)} />\
