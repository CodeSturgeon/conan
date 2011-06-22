#!/usr/bin/env python

import os
import sys
import json
import random
import string
import urllib2
import mimetypes
import base64

db_url = 'http://localhost:5984/conan'

file_name = sys.argv[1]

if not os.path.exists(file_name):
    print 'bad filename'
    sys.exit(1)

doc = {'doc_type':'download'}

with open(file_name) as f:
    content_type = mimetypes.guess_type(file_name)[0]
    if content_type == None: content_type = 'application/octet-stream'
    doc['_attachments'] = {
        os.path.basename(file_name):{
            'content_type': content_type,
            'data': base64.b64encode(f.read())
        }
    }

token = ''.join(random.choice(string.ascii_letters+string.digits) for x in range(15))

doc['tokens'] = {
    token: {
        'gen_time':'now',
        'use_time':'',
        'file_name':os.path.basename(file_name),
        'email':'nick@nickdafish.com',
        'name':'Nick Fisher'
    }
}

# FIXME - check for token collisions

req = urllib2.Request(db_url, json.dumps(doc))
req.add_header('Content-Type', 'application/json')
resp = urllib2.urlopen(req)
ret = json.loads(resp.read())

print "%s/_tokened_download/%s" % (db_url, token)

