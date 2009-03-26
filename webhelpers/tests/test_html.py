from webhelpers.html import literal, lit_sub, escape, HTML

def test_double_escape():
    quoted = escape(u'This string is "quoted"')
    assert quoted == u'This string is &quot;quoted&quot;'
    dbl_quoted = escape(quoted)
    assert quoted == dbl_quoted

def test_literal():
    lit = literal(u'This string <>')
    other = literal(u'<other>')
    assert u'This string <><other>' == lit + other
    assert type(lit + other) is literal
    
    assert u'&quot;<other>' == '"' + other
    assert u'<other>&quot;' == other + '"'
    
    mod = literal('<%s>ello')
    assert u'<&lt;H&gt;>ello' == mod % '<H>'
    assert type(mod % '<H>') is literal
    assert HTML('<a>') == '&lt;a&gt;'
    assert type(HTML('<a>')) is literal

def test_literal_dict():
    lit = literal(u'This string <>')
    unq = 'This has <crap>'
    sub = literal('%s and %s')
    assert u'This string <> and This has &lt;crap&gt;' == sub % (lit, unq)
    
    sub = literal('%(lit)s and %(lit)r')
    assert u"This string <> and literal(u'This string &lt;&gt;')" == sub % dict(lit=lit)
    sub = literal('%(unq)r and %(unq)s')
    assert u"'This has &lt;crap&gt;' and This has &lt;crap&gt;" == sub % dict(unq=unq)

def test_literal_mul():
    lit = literal(u'<>')
    assert u'<><><>' == lit * 3
    assert isinstance(lit*3, literal)

def test_literal_join():
    lit = literal(u'<>')
    assert isinstance(lit.join(['f', 'a']), literal)
    assert u'f<>a' == lit.join(('f', 'a'))

def test_literal_int():
    lit = literal(u'<%i>')
    assert u'<5>' == lit % 5

def test_html():
    a = HTML.a(href='http://mostlysafe\" <tag', c="Bad <script> tag")
    assert u'<a href="http://mostlysafe&quot; &lt;tag">Bad &lt;script&gt; tag</a>' == a
    
    img = HTML.img(src='http://some/image.jpg')
    assert u'<img src="http://some/image.jpg" />' == img
    
    br = HTML.br()
    assert u'<br />' == br

def test_lit_re():
    lit = literal('This is a <string>')
    unlit = 'This is also a <string>'
    
    result = lit_sub(r'<str', literal('<b'), lit)
    assert u'This is a <bing>' == escape(result)
    
    result = lit_sub(r'a <str', 'a <b> <b', unlit)
    assert u'This is also a &lt;b&gt; &lt;bing&gt;' == escape(result)

def test_unclosed_tag():
    result = HTML.form(_closed=False)
    print result
    assert u'<form>' == result
    
    result = HTML.form(_closed=False, action="hello")
    assert u'<form action="hello">' == result
