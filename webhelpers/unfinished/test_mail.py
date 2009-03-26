#!/usr/bin/env python

"""Test program to send mail to recipients.

Use the -s option with nose to have the verbose output logged and for the raw_input text to be displayed.

So, you run this test like this from the root of the webhelpers.mail package::
    
    ~/bin/nosetests test/test_mail.py -s 
"""
import sys; sys.path.append('../')
import webhelpers.mail

# Simulate a Pylons helpers setup
class H:
    mail = webhelpers.mail
h=H()

def setup():
    global address, ccaddress, bccaddress, smtp, username, password
    address = raw_input('Email address to recieve tests: ')
    ccaddress = raw_input('Email another address to recieve tests: ')
    bccaddress = raw_input('Email another address to recieve tests: ')
    smtp = raw_input('SMTP Server: ')
    username = raw_input('Username: ')
    password = raw_input('Password: ')

def test_sendmail_plain():
    h.mail.send(
        h.mail.plain(
            "Hi Jim\n\nHere's the photo from sendmail.\n\nJames",
            from_name = 'James Gardner',
            from_email = address,
            to=[address], 
            subject='Holiday Photos',
        ),
        sendmail='/usr/sbin/sendmail',
        verbose=True
    )

def test_sendmail_multi():
    h.mail.send(
        h.mail.multi(
            parts = [
                h.mail.part("Here is the photo from sendmail again.", content_type="text/plain", attach=False),
                h.mail.part(filename='test/attachment.jpg'),
            ],
            from_name = 'James Gardner',
            from_email = address,
            to=['Test Address <'+address+'>'], 
            cc=['Test Address CC <'+ccaddress+'>'], 
            bcc=['Test Address BCC <'+bccaddress+'>'], 
            subject='Holiday Photos',
        ),
        smtp=smtp,
        username=username,
        password = password,
        verbose=True,
    )

def test_smtp_plain():
    h.mail.send(
        h.mail.plain(
            "Hi Jim\n\nHere's the photo from SMTP.\n\nJames",
            from_name = 'James Gardner',
            from_email = address,
            to=[address], 
            subject='Holiday Photos',
        ),
        smtp=smtp,
        username=username,
        password = password,
        verbose=True,
    )
    
def test_smtp_multi():
    h.mail.send(
        h.mail.multi(
            parts = [
                h.mail.part("Here is the photo from SMTP again.", content_type="text/plain", attach=False),
                h.mail.part(filename='test/attachment.jpg'),
            ],
            from_name = 'James Gardner',
            from_email = address,
            to=['Test Address <'+address+'>'], 
            cc=['Test Address CC <'+ccaddress+'>'], 
            bcc=['Test Address BCC <'+bccaddress+'>'], 
            subject='Holiday Photos',
        ),
        smtp=smtp,
        username=username,
        password = password,
        verbose=True,
    )

def test_smtp_html():
    h.mail.send(
        h.mail.multi(
            parts = [
                h.mail.part("<html>This is an <b>html</b> email</html>", content_type="text/html", attach=False),
                h.mail.part(filename='test/attachment.jpg'),
            ],
            preamble='This is an HTML email but your email client does not support mulit-part emails.',
            from_name = 'James Gardner',
            from_email = address,
            to=[address], 
            subject='Holiday Photos',
        ),
        smtp=smtp,
        username=username,
        password = password,
        verbose=True,
    )

