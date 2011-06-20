#!/usr/bin/env python

import os
import sys
import json
import random
import string
import urllib2
import base64

file_name = sys.argv[1]
# FIXME
content_type = '!!FIXME!!'

doc = {}
doc['_attachments'] = {'file_name':{'content_type':content_type}}

token = ''.join(random.choice(string.ascii_letters+string.digits) for x in range(15))

doc['tokens'] = {token: {'generated':'now'} }

doc_id = '????'

print "http://localhost:5984/conan/_tokened_download/%s?token=%s" % (doc_id, token)

