#!/usr/bin/env python

import os
import sys
import datetime
import base64
import mimetypes
import hashlib
import urllib2
import json

db_url = 'http://localhost:5984/conan'

iso_now = datetime.datetime.utcnow().isoformat()+'Z'

# validate args
try:
    source_path = sys.argv[1]
except IndexError:
    print 'call this with a path'
    sys.exit(1)

if not os.path.exists(source_path):
    print 'bad filename'
    sys.exit(1)

# list files and md5
def load_file(path):
    f = {}
    f['content_type'] = mimetypes.guess_type(path)[0]
    if f['content_type'] == None:
        f['content_type'] = 'application/octet-stream'
    file_cont = open(path, 'rb').read()
    f['digest'] = 'md5-'+base64.b64encode(hashlib.md5(file_cont).digest())
    f['data'] = base64.b64encode(file_cont)
    return f

pub_files = {}
if os.path.isfile(source_path):
    pub_files[source_path] = load_file(source_path)
else:
    # ensure there is a trailing slash
    source_path = os.path.join(source_path, '')
    for root, dirs, files in os.walk(source_path):
        for f in files:
            f_path = os.path.join(root,f)
            f_vpath = f_path[len(source_path):]
            pub_files[f_vpath] = load_file(f_path)

# build metadata
doc = {
    'doc_type': 'publication',
    'versions': [
        {
            'files': dict([(f,pub_files[f]['digest']) for f in pub_files]),
            'source_path': source_path,
            'create_time': iso_now,
            'message': 'initial creation',
            'stub': 'test_pub'
        }
    ],
    '_attachments': pub_files
}

req = urllib2.Request(db_url, json.dumps(doc))
req.add_header('Content-Type', 'application/json')
resp = urllib2.urlopen(req)
ret = json.loads(resp.read())

print ret

# upload document
