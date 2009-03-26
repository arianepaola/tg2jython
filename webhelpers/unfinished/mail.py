"""\
Set of helpers to make sending email easier.

If you already have a ``Message`` based on the Python standard libraries
``email.message.Message`` you can send it like this::

    send(
        message, 
        smtp='smtp.example.com', 
        username='myusername', 
        password='mypassword'
    )

Or like this::

    send(message, sendmail='/usr/bin/sendmail')

If you have a message but haven't added key things like who it is to or from
you can add them like this::

    prepare(
        message,
        from_name = 'James Gardner',
        from_email = 'james@example.com',
        to=['Jeremey <jeremey@example.com>', 'kate@example.com'], 
        cc=[], 
        bcc=[], 
        subject='Test Email',
    )

If you haven't created a message at all and want a plain text email you can do
this::

    message_text = '''\
    Hi Jim,

    This is a simple plain text email.

    Regards, 

    James
    '''

    message = plain(message_text)

If you want a multi-part message for attaching files etc you generate it
slightly differently:

    message_text = '''\
    Hi Jim,

    Here is my holiday photo.

    Regards, 

    James
    '''

    message = multi(
        preamble = 'Only non-MIME aware email clients see this text',
        parts = [
            part(message_text, content_type='text/plain'),
            part(filename='photo.jpg'),
        ],
    )
    
Putting this all togehter you can do it all at once like this::

    send(
        prepare(
            plain("Hi Jim\nHere's the photo.\n\nJames"),
            from_name = 'James Gardner',
            from_email = 'james@example.com',
            to=['Jeremey <jeremey@example.com>'], 
            subject='Holiday Photos',
        ),
        sendmail='/usr/bin/sendmail',
    )
"""

from email import Utils
import mimetypes
import os
import smtplib

from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email import Encoders

class MailError(Exception):
    "Generic problem buidling a message or sending a mail"

def _prepare(
    message,
    from_name,
    from_email,
    to=[], 
    cc=[], 
    bcc=[], 
    subject='(no subject)',
):
    if not to and not cc and not bcc:
        raise MailError("No recipients specified")
    message['From'] = Utils.formataddr((from_name, from_email))
    message['Subject'] = subject
    if isinstance(to, (unicode, str)):
        to=[to]
    if to:
        message['To'] = ', '.join(to)
    if isinstance(cc, (unicode, str)):
        cc=[cc]
    if cc:
        message['Cc'] = ', '.join(cc)
    if isinstance(bcc, (unicode, str)):
        bcc=[bcc]
    if bcc:
        message['Bcc'] = ', '.join(bcc)
    return message

def plain(
    text,
    type='plain',
    charset=None,
    **prepare_options
):
    """
    
    ``**prepare_options`` 
        Any extra keyword argument are sent to ``_prepare()`` to add standard 
        information to the message.
    """
    if charset is None:
        message = MIMEText(text, type)
    else:
        message = MIMEText(text, type, charset)
    if prepare_options:
        message = _prepare(message, **prepare_options)
    return message

def part(
    data=None,
    filename=None,
    content_type=None,
    attach=True,
):
    """\
    Create a MIME part to include in the message.

    ``data`` 
        The data to include. If not specified the contents of the file
        specified by ``filename`` are used.

    ``filename``
        The filename of the file to use for the data if ``data`` is not
        specified. If ``attach`` is ``True`` this filename is used as the
        filename of the attachment in the resulting email.

    ``content_type`` 
        The content type of the part, for example ``"text/plain"``. If not
        specified the content type will be guessed from the filename.

    ``attach``
        If ``True`` the part will be set up as an attachment. This is probably
        what you want for photos and the like but not what you want for plain
        text attachments which you want treated as the body of the email.
    """
    if not filename and not data:
        raise MailError("You must specify a filename or some data")
    if filename and not content_type:
        main_type, sub_type = mimetypes.guess_type(filename)
    elif not content_type:
        raise MailError("Please specify a content type")
    else:
        main_type, sub_type = content_type.split('/')
    if filename and not data:
        fp = open(filename, 'rb')
        data = fp.read()
        fp.close()
    part = MIMEBase(main_type, sub_type)
    part.set_payload(data)
    Encoders.encode_base64(part)
    if attach:
        if filename:
            # Set the filename parameter
            part.add_header(
                'Content-Disposition',
                'attachment',
                filename=filename.replace('\\','/').strip('/').split('/')[-1],
            )
        else:
            part.add_header('Content-Disposition', 'attachment')
    return part

def multi(
    preamble = None,
    parts = [],
    **prepare_options
):
    """\
    Assemble a multi-part MIME message.

    ``preamble``
        Text to display before the message parts which will be seen only by
        email clients which don't support MIME.

    ``parts``
        A list of the MIME parts to add to this message. You can use ``part()``
        to create each part.

    ``**prepare_options`` 
        Any extra keyword argument are sent to ``_prepare()`` to add standard 
        information to the message.
    
    """
    message = MIMEMultipart()
    if preamble is not None:
        message.preamble = preamble
    for part in parts:
        message.attach(part)
    if prepare_options:
        message = _prepare(message, **prepare_options)
    return message

def send(
    message,
    smtp=None, 
    username=None,
    password=None,
    port=None,
    verbose=False,
    sendmail=None,
):
    """\
    Send an email message via SMTP or Sendmail.

    Whether to send the message via sendmail or SMTP is determined by
    whether you specify an SMTP server address or a sendmail path. You 
    should not specify both.

    ``smtp``
        The SMTP server address you want to use to send the mail. You
        should not specify both ``sendmail`` and ``smtp``.

    ``username``
        The username for the SMTP server, if required.

    ``password``
        The password for the SMTP server, if required.

    ``port``
        The SMTP server's port, if required.

    ``verbose``
        Set to ``True`` if you want all manner of information displayed 
        spewed out for debugging.

    ``sendmail``
       Path to the sendmail binary (or sendmail compatible binary) which is
       usually something like ``/usr/bin/sendmail`` or ``/usr/sbin/sendmail``
       or ``/usr/local/bin/sendmail``. You should not specify both ``sendmail``
       and ``smtp``.
    """    
    if sendmail and smtp:
        raise MailError("Please specify either sendmail or smtp, not both")
    if not sendmail and not smtp:
        raise MailError("You must specify an SMTP server or Sendmail binary path")
    if sendmail:
        # No further processing required, sendmail handles the rest
        if not os.path.exists(sendmail):
            raise MailError(
                "The path '%s' doesn't exist. Please check the location of "
                "sendmail."%(
                    sendmail
                )
            )
        data = message.as_string()
        print data
        cmd = sendmail+" -t"
        if verbose:
            cmd+= " -v"
        fp = os.popen(cmd, 'w')
        fp.write(data)
        error = fp.close()
        if error:
            raise MailError("Error sending mail: Sendmail Error '%s'."% error)
    else:
        # We are using SMTP
        s = smtplib.SMTP()
        if verbose:
            s.set_debuglevel(100)
        if port:
           s.connect(smtp, port)
        else:
            s.connect(smtp)
        if username:
            s.login(username, password)
        all = []
        if message['To']:
            to = message['To'].strip().strip(',').split(',')
            for address in to:
                if address:
                    all.append(address)
        if message['Cc']:
            cc = message['Cc'].strip().strip(',')
            for address in cc.split(','):
                if address:
                    all.append(address)
        if message['Bcc']:
            bcc = message['Bcc'].strip().strip(',')
            for address in bcc.split(','):
                if address:
                    all.append(address)
        # Let's remove the Bcc part just to make sure:
        message['Bcc'] = ''
        result = s.sendmail(message['From'], all, message.as_string())
        s.quit()
        if result:
            for r in result.keys():
                error+= "Error sending to"+ str(r)
                rt = result[r]
                error+= "Code"+ str(rt[0])+":"+ str(rt[1])
            raise MailError("Error sending mail: %s"% error)

