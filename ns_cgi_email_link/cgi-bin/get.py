#!/usr/bin/python

import sys, os, time
import cgi, hashlib, smtplib, Cookie

#cgi.test()

print 'Content-type: text/plain\n\n'

C = Cookie.SimpleCookie()
C.load(os.environ["HTTP_COOKIE"])
d = cgi.parse()
path = 'htdoc/%s.html' % d["token"][0]
try:
    expire_date = C["token"]["expires"]
except KeyError:
    print "HTTP Error 403: access forbidden"

expires = time.mktime(time.strptime(expire_date, "%a, %d %b %Y %H:%M:%S GMT"))
if expires < time.time():
    print "Permission to access has expired"
try:
    f = file(path)
except IOError:
    print "HTTP Error 404: file not found"

# Ok, present document

print 'Document '+path+':'
print 'Expires '+expire_date
sys.stdout.write(f.read())






