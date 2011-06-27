#!/usr/bin/env python

import urllib2
import re
import json
import datetime
from conan import gen_token
import sys

email = 'nick@nickdafish.com'
name = 'Nick Fisher'
pattern = '.*'
pub_id = '2a7e9560611a11950f2da4aeed01c68b'

db_url = 'http://localhost:5984/conan'
iso_now = datetime.datetime.utcnow().isoformat()+'Z'

pattern_re = re.compile(pattern)
# get list of files in that publication
pub_files = {}

files_view_url = "%s/_design/conan/_view/files?startkey=\"[%s,]\"&endkey=[\"%s\",{}]"%(db_url,pub_id,pub_id)
files_view_ret = json.loads(urllib2.urlopen(files_view_url).read())


tok_files = []

for row in files_view_ret['rows']:
    file_name = row['key'][1]
    if pattern_re.match(file_name):
        tok_files.append(file_name)

doc = {
    'doc_type': 'distribution',
    'publication_id': pub_id,
    'addresses': {
        email: {
            'name':name,
            'pattern':pattern,
            'files': tok_files,
            'tokens': {
                gen_token(): {
                    'gen_time': iso_now,
                }
            }
        }
    }
}

req = urllib2.Request(db_url, json.dumps(doc))
req.add_header('Content-Type', 'application/json')
resp = urllib2.urlopen(req)
ret = json.loads(resp.read())

print ret
