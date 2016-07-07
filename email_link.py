#!/usr/bin/python
'''Sends MIME message to SMTP server, where message contains a link to
a dynamically generated page that expires in 24 hours. Data for
creating and sending message obtained from POST data (CGI).
'''

import sys, os, time
import cgi, hashlib, smtplib, Cookie

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

dft_sender='do_not_reply@neuroscouting.com'
smtp_addr = 'localhost:8025'
dft_docd = 'htdoc'

def gen_doc_path(msg, docd=None):
    '''Generate the document filename from and md5 digest of the
    argument msg
    '''
    x = hashlib.md5(msg)
    if not docd:
        docd = dft_docd
    path = '%s/%s.html' % (docd, x.hexdigest())
    return path

def gen_doc_link(path):
    '''Generate link to the argument file path'''
    h = os.environ.get('SERVER_HOST','localhost')
    p = os.environ.get('SERVER_PORT','8000')
    k = os.path.split(os.path.splitext(path)[0])[-1]
    u = 'http://%s:%s/get?token=%s' % (h, p, k)
    return u

def gen_msg_parts(link):
    '''Create the body of the email message, plain text and html,
    each containing the link URL'''
    text = "Here is the link you requested:\n" + link + \
           "\nValid for 24 hours.\n"
    html = """\
<html>
  <head>
    <title>Custom link</title>
  </head>
  <body>
    <p>
      Here is the <a href=\"%s\">link</a> you requested.<br>
Valid for 24 hours.
    </p>
  </body>
</html>
""" % link
    return text, html

def gen_mime_msg(addr, link, sender=None):
    '''Build a MIME message for email delivery
    addr is the destination email address
    link is the generated URL for the document
    Optionally set the sender address
    '''
    me = sender or dft_sender
    assert (isinstance(
        addr, basestring) and addr.find('@') > 0), "bad email address"
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "NeuroScouting link"
    msg['From'] = me
    msg['To'] = addr
    
    # Create the body of the message (a plain-text and an HTML version).
    text, html = gen_msg_parts(link)
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    #sys.stderr.write('\ngen_mime_msg: msg='+str(msg))
    return msg

def send_mime_msg(msg):
    '''Send the argument MIME message via SMTP server'''
    host, port = smtp_addr.split(':')
    s = smtplib.SMTP(host, port)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()

def send_head(path, now):
    C = Cookie.SimpleCookie()
    p, t = os.path.split(path)
    C["Token"] = t
    C["Token"]["expires"] = Cookie._getdate(future=86400)
    p = os.path.splitext(p)[0]
    if not p.startswith(os.path.sep):
        p = '/'+p
    C["Token"]["path"] = p
    print C

def send_content(addr):
    sys.stdout.write('''Content-type: text/plain

The link has been emailed to ''' + addr + '''
'''
    )                     

def run(addr):
    '''Sends a generated link to destination email address'''
    now = time.time()
    path = gen_doc_path(addr+str(now))
    link = gen_doc_link(path) # uniq hash data
    send_mime_msg(gen_mime_msg(addr, link)) # addr is email recipient
    file(path, 'w').write('created for %s at %s\n' % (addr, time.ctime(now)))
    send_head(path, now)
    send_content(addr)
    return link

def main():
  global smtp_addr # mail sender, host:port
  d = cgi.parse()
  if 'smtp_addr' in d:
      smtp_addr = d['smtp_addr'][0]
  if 'addr' in d:
      run(d['addr'][0])

if __name__ == '__main__':
  main()
  sys.exit(0)
