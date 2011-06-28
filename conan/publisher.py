#!/usr/bin/env python

import os
import sys
import datetime
import base64
import mimetypes
import hashlib
import urllib2
import json
from optparse import OptionParser

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

def main():
    usage = "usage: %prog [options] path_to_publish"
    parser = OptionParser()
    parser.add_option('--host', dest="db_host", default='localhost',
                      help='Hostname of the CouchDB server')
    parser.add_option('--port', dest="db_port", default='5984',
                      help='Port of the CouchDB server')
    parser.add_option('--db', dest='db_name', default='conan',
                      help='Database to use in CouchDB')
    (options, args) = parser.parse_args()

    # validate args
    if len(args) != 1:
        print "!!wrong no of arguments detected, exiting!!\n"
        parser.print_help()
        sys.exit(1)

    source_path = args[0]
    if not os.path.exists(source_path):
        print "!!bad path supplied!!\n"
        parser.print_help()
        sys.exit(1)

    db_url = "http://%s:%s/%s"%(options.db_host, options.db_port,
                                options.db_name)

    # assemble files
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
                'create_time': datetime.datetime.utcnow().isoformat()+'Z',
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
    if resp.code == 201:
        print 'Files published'
        print "Publication ID:", ret['id']
    else:
        print 'Something went wrong with the publish...'
        print ret
        sys.exit(2)

if __name__ == "__main__":
    main()
