#!/usr/bin/env python

import os
import sys
import json
import random
import string
import urllib2
import mimetypes
import base64

file_name = sys.argv[1]

if not os.path.exists(file_name):
    print 'bad filename'
    sys.exit(1)

doc = {}

with open(file_name) as f:
    content_type = mimetypes.guess_type(file_name)[0]
    if content_type == None: content_type = 'application/octet-stream'
    doc['_attachments'] = {
            file_name:{
                'content_type': content_type,
                'data': base64.b64encode(f.read())
            }
    }

token = ''.join(random.choice(string.ascii_letters+string.digits) for x in range(15))

doc['tokens'] = {token: {'generated':'now'} }

req = urllib2.Request('http://localhost:5984/conan', json.dumps(doc))
req.add_header('Content-Type', 'application/json')
resp = urllib2.urlopen(req)
ret = json.loads(resp.read())

doc_id = ret['id']

print ret

print "http://localhost:5984/conan/_tokened_download/%s?token=%s" % (doc_id, token)

