<%namespace name="tw" module="tw.core.mako_util"/>\
<form ${tw.attrs(
    [('id', context.get('id')),
     ('name', name),
     ('action', action),
     ('method', method),
     ('class', css_class)],
    attrs=attrs
)}>
    <div>
    % for field in hidden_fields:
        ${field.display(value_for(field), **args_for(field))}
    % endfor
    % for field in fields:
        ${field.display(value_for(field), **args_for(field))} <br />
    % endfor
    </div>
</form>\
