from webhelpers.htmlgen import html

def test_html():
    assert html('<foo>') == '<foo>'
    assert html.escape('<foo>') == '&lt;foo&gt;'
    assert str(html.br) == '<br />'
    assert html.a(href='url', c='whatever') == '<a href="url">whatever</a>'
    assert html.a('whatever', href='url', class_=None) == '<a href="url">whatever</a>'
    assert html.a(a=1, b=2, c_=3) == '<a a="1" b="2" c="3"></a>'
    
