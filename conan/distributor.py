#!/usr/bin/env python

import urllib2
import re
import json
import datetime
from conan import gen_token
import sys

email = 'nick@nickdafish.com'
name = 'Nick Fisher'
pattern = '_.*'
pub_id = '2a7e9560611a11950f2da4aeed01c68b'

db_url = 'http://localhost:5984/conan'
iso_now = datetime.datetime.utcnow().isoformat()+'Z'

pattern_re = re.compile(pattern)
# get list of files in that publication
pub_files = {}

files_view_url = "%s/_design/conan/_view/files?startkey=\"[%s,]\"&endkey=[\"%s\",{}]"%(db_url,pub_id,pub_id)
print files_view_url
files_view_ret = json.loads(urllib2.urlopen(files_view_url).read())


print files_view_ret['rows']
tok_files = []

for row in files_view_ret['rows']:
    print "\nrow:\n",row
    file_name = row['key'][1]
    if pattern_re.match(file_name):
        tok_files.append(file_name)

print 'done'
doc = {
    'doc_type': 'distribution',
    'pub_id': pub_id,
    'addresses': {
        email: {
            'name':name,
            'files': tok_files,
            'tokens': {
                gen_token(): {
                    'gen_time': iso_now,
                    'files': tok_files
                }
            }
        }
    }
}
print "ddddddd\n",doc
