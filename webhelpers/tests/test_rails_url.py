from util import WebHelpersTestCase
import unittest

from webhelpers.rails.urls import *
from routes import *

class TestURLHelper(WebHelpersTestCase):
    def test_button_to_with_straight_url(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input type=\"submit\" value=\"Hello\" /></div></form>", 
               button_to("Hello", "http://www.example.com"))

    def test_button_to_with_query(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com/q1=v1&amp;q2=v2\" class=\"button-to\"><div><input type=\"submit\" value=\"Hello\" /></div></form>", 
               button_to("Hello", "http://www.example.com/q1=v1&q2=v2"))

    def test_button_to_with_escaped_query(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com/q1=v1&amp;q2=v2\" class=\"button-to\"><div><input type=\"submit\" value=\"Hello\" /></div></form>",
                         button_to("Hello", "http://www.example.com/q1=v1&amp;q2=v2"))
    
    def test_button_to_with_query_and_no_name(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com?q1=v1&amp;q2=v2\" class=\"button-to\"><div><input type=\"submit\" value=\"http://www.example.com?q1=v1&amp;q2=v2\" /></div></form>", 
               button_to(None, "http://www.example.com?q1=v1&q2=v2"))
    
    def test_button_to_with_javascript_confirm(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input onclick=\"return confirm('Are you sure?');\" type=\"submit\" value=\"Hello\" /></div></form>",
               button_to("Hello", "http://www.example.com", confirm="Are you sure?"))
    
    def test_button_to_enabled_disabled(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input type=\"submit\" value=\"Hello\" /></div></form>",
               button_to("Hello", "http://www.example.com", disabled=False))
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input disabled=\"disabled\" type=\"submit\" value=\"Hello\" /></div></form>",
               button_to("Hello", "http://www.example.com", disabled=True))
    
    def test_button_to_with_method_delete(self):
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input id=\"_method\" name=\"_method\" type=\"hidden\" value=\"DELETE\" /><input type=\"submit\" value=\"Hello\" /></div></form>", 
            button_to("Hello", "http://www.example.com", method='DELETE'))
        self.assertEqual("<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input id=\"_method\" name=\"_method\" type=\"hidden\" value=\"delete\" /><input type=\"submit\" value=\"Hello\" /></div></form>", 
            button_to("Hello", "http://www.example.com", method='delete'))

    def test_button_to_with_method_get(self):
        self.assertEqual("<form method=\"get\" action=\"http://www.example.com\" class=\"button-to\"><div><input type=\"submit\" value=\"Hello\" /></div></form>",
            button_to("Hello", "http://www.example.com", method='get'))
        self.assertEqual("<form method=\"GET\" action=\"http://www.example.com\" class=\"button-to\"><div><input type=\"submit\" value=\"Hello\" /></div></form>",
            button_to("Hello", "http://www.example.com", method='GET'))

    def test_button_to_with_img(self):
        self.assertEqual('<form method="POST" action="/content/edit/3" class="button-to"><div><input alt="Edit" src="/images/icon_delete.gif" type="image" value="Edit" /></div></form>',
                         button_to("Edit", url(action='edit', id=3), type='image', src='icon_delete.gif'))
        self.assertEqual('<form method="POST" action="/content/submit/3" class="button-to"><div><input alt="Complete the form" src="/images/submit.png" type="image" value="Submit" /></div></form>',
                         button_to("Submit", url(action='submit', id=3), type='image', src='submit', alt='Complete the form'))

    def test_link_tag_with_straight_url(self):
        self.assertEqual("<a href=\"http://www.example.com\">Hello</a>", link_to("Hello", "http://www.example.com"))
    
    def test_link_tag_with_query(self):
        self.assertEqual("<a href=\"http://www.example.com?q1=v1&amp;q2=v2\">Hello</a>", 
               link_to("Hello", "http://www.example.com?q1=v1&q2=v2"))
    
    def test_link_tag_with_query_and_no_name(self):
        self.assertEqual("<a href=\"http://www.example.com?q1=v1&amp;q2=v2\">http://www.example.com?q1=v1&amp;q2=v2</a>", 
               link_to(None, "http://www.example.com?q1=v1&q2=v2"))
    
    def test_link_tag_with_custom_onclick(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"alert('yay!')\">Hello</a>", 
               link_to("Hello", "http://www.example.com", onclick="alert('yay!')"))
    
    def test_link_tag_with_javascript_confirm(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"return confirm('Are you sure?');\">Hello</a>",
               link_to("Hello", "http://www.example.com", confirm="Are you sure?"))
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"return confirm('You can\\'t possibly be sure, can you?');\">Hello</a>", 
               link_to("Hello", "http://www.example.com", confirm="You can't possibly be sure, can you?"))
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"return confirm('You can\\'t possibly be sure,\\n can you?');\">Hello</a>", 
               link_to("Hello", "http://www.example.com", confirm="You can't possibly be sure,\n can you?"))
    
    def test_link_tag_with_popup(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"window.open(this.href);return false;\">Hello</a>",
               link_to("Hello", "http://www.example.com", popup=True))
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"window.open(this.href);return false;\">Hello</a>", 
               link_to("Hello", "http://www.example.com", popup='true'))
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"window.open(this.href,'window_name','width=300,height=300');return false;\">Hello</a>", 
               link_to("Hello", "http://www.example.com", popup=['window_name', 'width=300,height=300']))
    
    def test_link_tag_with_popup_and_javascript_confirm(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"if (confirm('Fo\\' sho\\'?')) { window.open(this.href); };return false;\">Hello</a>",
               link_to("Hello", "http://www.example.com", popup=True, confirm="Fo' sho'?" ))
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"if (confirm('Are you serious?')) { window.open(this.href,'window_name','width=300,height=300'); };return false;\">Hello</a>",
               link_to("Hello", "http://www.example.com", popup=['window_name', 'width=300,height=300'],
                       confirm="Are you serious?"))
    
    def test_link_tag_using_post_javascript(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"var f = document.createElement('form'); f.style.display = 'none'; this.parentNode.appendChild(f); f.method = 'POST'; f.action = this.href;f.submit();return false;\">Hello</a>",
               link_to("Hello", "http://www.example.com", post=True))
    
    def test_link_tag_using_delete_javascript(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"var f = document.createElement('form'); f.style.display = 'none'; this.parentNode.appendChild(f); f.method = 'POST'; f.action = this.href;var m = document.createElement('input'); m.setAttribute('type', 'hidden'); m.setAttribute('name', '_method'); m.setAttribute('value', 'DELETE'); f.appendChild(m);f.submit();return false;\">Destroy</a>",
                link_to("Destroy", "http://www.example.com", method='DELETE'))
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"var f = document.createElement('form'); f.style.display = 'none'; this.parentNode.appendChild(f); f.method = 'POST'; f.action = this.href;var m = document.createElement('input'); m.setAttribute('type', 'hidden'); m.setAttribute('name', '_method'); m.setAttribute('value', 'delete'); f.appendChild(m);f.submit();return false;\">Destroy</a>",
                link_to("Destroy", "http://www.example.com", method='delete'))

    def test_link_tag_using_post_javascript_and_confirm(self):
        self.assertEqual("<a href=\"http://www.example.com\" onclick=\"if (confirm('Are you serious?')) { var f = document.createElement('form'); f.style.display = 'none'; this.parentNode.appendChild(f); f.method = 'POST'; f.action = this.href;f.submit(); };return false;\">Hello</a>",
               link_to("Hello", "http://www.example.com", post=True, confirm="Are you serious?"))
        self.assertRaises(ValueError, lambda: \
                          link_to("Hello", "http://www.example.com", post=True, popup=True, confirm="Are you serious?"))

    def test_link_to_unless_current(self):
        self.assertEqual('Click Here',
                         link_to_unless_current('Click Here',
                                                '/test?test=webhelpers&framework=pylons'))
        self.assertEqual('<a href="/test?test=routes&amp;framework=pylons">Click Here</a>',
                         link_to_unless_current('Click Here',
                                                '/test?test=routes&framework=pylons'))
        self.assertEqual('<a href="/test2?test=webhelpers&amp;framework=pylons">Click Here</a>',
                         link_to_unless_current('Click Here',
                                                '/test2?test=webhelpers&framework=pylons'))
    
    def test_link_to_unless(self, func=link_to_unless):
        condition = func == link_to_unless and True or False
        self.assertEqual('Click Here',
                         func(condition, 'Click Here',
                                        '/test?test=webhelpers&framework=pylons'))
        self.assertEqual('<a href="/test?test=webhelpers&amp;framework=pylons">Click Here</a>',
                         func(not condition, 'Click Here',
                                        '/test?test=webhelpers&framework=pylons'))
        self.assertEqual('<a href="/test?test=routes&amp;framework=pylons">Click Here</a>',
                         func(not condition, 'Click Here',
                                        '/test?test=routes&framework=pylons'))
        self.assertEqual('Click Here',
                         func(condition, 'Click Here',
                                        '/test2?test=webhelpers&framework=pylons'))

    def test_link_to_if(self):
        self.test_link_to_unless(func=link_to_if)

    def test_mail_to(self):
        self.assertEqual('<a href="mailto:justin@example.com">justin@example.com</a>', mail_to("justin@example.com"))
        self.assertEqual('<a href="mailto:justin@example.com">Justin Example</a>', mail_to("justin@example.com", "Justin Example"))
        self.assertEqual('<a class="admin" href="mailto:justin@example.com">Justin Example</a>',
                         mail_to("justin@example.com", "Justin Example", class_="admin"))

    def test_mail_to_with_javascript(self):
        self.assertEqual("<script type=\"text/javascript\">\n//<![CDATA[\neval(unescape('%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%6d%65%40%64%6f%6d%61%69%6e%2e%63%6f%6d%22%3e%4d%79%20%65%6d%61%69%6c%3c%2f%61%3e%27%29%3b'))\n//]]>\n</script>", mail_to("me@domain.com", "My email", encode = "javascript"))

    def test_mail_to_with_options(self):
        self.assertEqual('<a href="mailto:me@example.com?cc=ccaddress%40example.com&amp;bcc=bccaddress%40example.com&amp;subject=This%20is%20an%20example%20email&amp;body=This%20is%20the%20body%20of%20the%20message.">My email</a>',
            mail_to("me@example.com", "My email", cc="ccaddress@example.com",
                    bcc="bccaddress@example.com", subject="This is an example email",
                    body="This is the body of the message."))

    def test_mail_to_with_img(self):
        self.assertEqual('<a href="mailto:feedback@example.com"><img src="/feedback.png" /></a>',
                        mail_to('feedback@example.com', '<img src="/feedback.png" />'))

    def test_mail_to_with_hex(self):
        self.assertEqual("<a href=\"&#109;&#97;&#105;&#108;&#116;&#111;&#58;%6d%65@%64%6f%6d%61%69%6e.%63%6f%6d\">My email</a>",
                         mail_to("me@domain.com", "My email", encode = "hex"))
        self.assertEqual("<a href=\"&#109;&#97;&#105;&#108;&#116;&#111;&#58;%6d%65@%64%6f%6d%61%69%6e.%63%6f%6d\">&#109;&#101;&#64;&#100;&#111;&#109;&#97;&#105;&#110;&#46;&#99;&#111;&#109;</a>",
                         mail_to("me@domain.com", None, encode = "hex"))

    def test_mail_to_with_replace_options(self):
        self.assertEqual('<a href="mailto:wolfgang@stufenlos.net">wolfgang(at)stufenlos(dot)net</a>',
                        mail_to("wolfgang@stufenlos.net", None, replace_at="(at)", replace_dot="(dot)"))
        self.assertEqual("<a href=\"&#109;&#97;&#105;&#108;&#116;&#111;&#58;%6d%65@%64%6f%6d%61%69%6e.%63%6f%6d\">&#109;&#101;&#40;&#97;&#116;&#41;&#100;&#111;&#109;&#97;&#105;&#110;&#46;&#99;&#111;&#109;</a>",
                         mail_to("me@domain.com", None, encode = "hex", replace_at = "(at)"))
        self.assertEqual("<a href=\"&#109;&#97;&#105;&#108;&#116;&#111;&#58;%6d%65@%64%6f%6d%61%69%6e.%63%6f%6d\">My email</a>",
                         mail_to("me@domain.com", "My email", encode = "hex", replace_at = "(at)"))
        self.assertEqual("<a href=\"&#109;&#97;&#105;&#108;&#116;&#111;&#58;%6d%65@%64%6f%6d%61%69%6e.%63%6f%6d\">&#109;&#101;&#40;&#97;&#116;&#41;&#100;&#111;&#109;&#97;&#105;&#110;&#40;&#100;&#111;&#116;&#41;&#99;&#111;&#109;</a>",
                         mail_to("me@domain.com", None, encode = "hex", replace_at = "(at)", replace_dot = "(dot)"))
        self.assertEqual("<script type=\"text/javascript\">\n//<![CDATA[\neval(unescape('%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%6d%65%40%64%6f%6d%61%69%6e%2e%63%6f%6d%22%3e%4d%79%20%65%6d%61%69%6c%3c%2f%61%3e%27%29%3b'))\n//]]>\n</script>",
                         mail_to("me@domain.com", "My email", encode = "javascript", replace_at = "(at)", replace_dot = "(dot)"))

    def test_current_page(self):
        self.assertEqual(True, (current_page('/test?test=webhelpers&framework=pylons')))
        self.assertEqual(True, current_page(url('/test?test=webhelpers&framework=pylons')))

    def test_current_url(self):
        self.assertEquals('/test?test=webhelpers&framework=pylons', current_url())
        self.assertEquals(True, isinstance(current_url(), str))

if __name__ == '__main__':
    suite = [unittest.makeSuite(TestURLHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
