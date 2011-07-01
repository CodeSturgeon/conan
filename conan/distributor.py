#!/usr/bin/env python

import urllib2
import re
import json
import datetime
from conan import gen_token
import conan.email
import sys
from optparse import OptionParser

def main():
    usage = "usage: %prog [options] pub_id email_addr pattern"
    parser = OptionParser(usage)
    parser.add_option('--host', dest="db_host", default='localhost',
                      help='Hostname of the CouchDB server')
    parser.add_option('--port', dest="db_port", default='5984',
                      help='Port of the CouchDB server')
    parser.add_option('--db', dest='db_name', default='conan',
                      help='Database to use in CouchDB')
    (options, args) = parser.parse_args()

    # validate args
    if len(args) != 3:
        print "!!wrong no of arguments detected, exiting!!\n"
        parser.print_help()
        sys.exit(1)

    pub_id = args[0]
    email = args[1]

    pattern = args[2]
    pattern_re = re.compile(pattern)

    db_url = "http://%s:%s/%s"%(options.db_host, options.db_port,
                                options.db_name)

    name = '_name feature pending_'

    # Load config... currently only used for email
    cfg = json.loads(urllib2.urlopen("%s/conan_config"%db_url).read())

    # get list of files in that publication
    pub_files = {}

    files_view_url  = "%s/_design/conan/_view/publication_files"%db_url
    files_view_url += "?startkey=[\"%s\",]&endkey=[\"%s\",{}]"%(pub_id,pub_id)
    files_view_ret = json.loads(urllib2.urlopen(files_view_url).read())

    if len(files_view_ret['rows']) == 0:
        print 'publication not found'
        sys.exit(1)

    tok_files = []

    for row in files_view_ret['rows']:
        file_name = row['key'][1]
        if pattern_re.match(file_name):
            tok_files.append(file_name)

    if len(tok_files) == 0:
        print 'pattern matched no files'
        sys.exit(1)

    token = gen_token()

    doc = {
        'doc_type': 'distribution',
        'publication_id': pub_id,
        'addresses': {
            email: {
                'name':name,
                'pattern':pattern,
                'files': tok_files,
                'tokens': {
                    token: {
                        'gen_time': datetime.datetime.utcnow().isoformat()+'Z'
                    }
                }
            }
        }
    }

    req = urllib2.Request(db_url, json.dumps(doc))
    req.add_header('Content-Type', 'application/json')
    resp = urllib2.urlopen(req)
    ret = json.loads(resp.read())
    if resp.code == 201:
        print 'Distribution created'
        print "Distribution ID:", ret['id']
        print 'Token:', token
    else:
        print 'Something went wrong with the creation of the dist doc...'
        print ret
        sys.exit(2)

    conan.email.configure(cfg)
    conan.email.send_token(email ,name, token)

if __name__ == "__main__":
    main()
