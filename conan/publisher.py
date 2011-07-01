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
from conan import gen_token
import conan.email

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
    parser.add_option('-r', '--restate', dest='restate', default=False,
                      action='store_true',
                      help='Restate files rather than publish as new')
    (options, args) = parser.parse_args()

    iso_now = datetime.datetime.utcnow().isoformat()+'Z'

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

    # search for and warn about files that start with a _
    # CouchDB has inconsistant handling of these files
    # https://issues.apache.org/jira/browse/COUCHDB-1210
    for filename in pub_files.keys():
        if filename.startswith('_'):
            print 'leading underscores are not allowed:', filename
            sys.exit(2)

    # look for the files in previous publications
    files_req = urllib2.Request("%s/_design/conan/_view/published_files"%db_url)
    files_req.get_method = lambda: 'POST'
    files_req.add_data(json.dumps({"keys":pub_files.keys()}))
    files_req.add_header('Content-Type', 'application/json')
    files_ret = json.loads(urllib2.urlopen(files_req).read())
    files_previous = files_ret['rows']

    if not options.restate:
        # Take care of easyiest case first
        if len(files_previous) != 0:
            print 'some files have been previously published - aborting'
            sys.exit(2)
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
        print json.dumps(doc, indent=2); sys.exit()
        req = urllib2.Request(db_url, json.dumps(doc))
        req.add_header('Content-Type', 'application/json')
        resp = urllib2.urlopen(req)
        ret = json.loads(resp.read())
        if resp.code == 201:
            print 'Files published'
            print "Publication ID:", ret['id']
            sys.exit()
        else:
            print 'Something went wrong with the publish...'
            print ret
            sys.exit(2)

    # If we got here, we are restating files

    # if pub_files not in files_previous raise error
    # if pub_files spans publicatiuons raise error
    pub_keys = pub_files.keys()
    upd_pub = ''

    # Publication checking
    for prev_data in files_previous:
        if upd_pub == '':
            upd_pub = prev_data['id']
        if upd_pub != prev_data['id']:
            print 'files span publications'
            sys.exit(2)

        pub_keys.remove(prev_data['key'])

    if len(pub_keys) != 0:
        print 'some files not found in previous publication!'
        print pub_keys
        sys.exit(2)

    # consult md5s to see what changed

    # ammend publication
    pub_req = urllib2.Request("%s/%s"%(db_url,upd_pub))
    pub = json.loads(urllib2.urlopen(pub_req).read())
    pub['_attachments'].update(pub_files)

    pub_req.get_method = lambda: 'PUT'
    pub_req.add_data(json.dumps(pub))
    pub_req.add_header('Content-Type', 'application/json')
    pub_ret = urllib2.urlopen(pub_req)

    # find who has downloaded these files
    dls_req = urllib2.Request("%s/_design/conan/_view/downloaded_files?group=true"%db_url)
    dls_req.get_method = lambda: 'POST'
    dls_req.add_data(json.dumps({"keys":pub_files.keys()}))
    dls_req.add_header('Content-Type', 'application/json')
    dls_ret = json.loads(urllib2.urlopen(dls_req).read())
    dls_infos = dls_ret['rows']

    # get tokens to anyone who downloaded the restated files
    if len(dls_infos) != 0:
        addrs = {}

        # generate file lists and tokens
        for dl_info in dls_infos:
            filename = dl_info['key']
            for addr_data in dl_info['value']:
                addr = addr_data[0]
                if not addrs.has_key(addr):
                    addrs[addr] = {
                        'name': addr_data[1],
                        'tokens': {
                            gen_token(): {
                                'gen_time': iso_now
                            }
                        },
                        'files': []
                    }
                addrs[addr]['files'].append(filename)


        # make new distribution doc
        doc = {
            'doc_type': 'distribution',
            'publication_id': upd_pub,
            'addresses': addrs
        }
        req = urllib2.Request(db_url, json.dumps(doc))
        req.add_header('Content-Type', 'application/json')
        resp = urllib2.urlopen(req)
        ret = json.loads(resp.read())
        # FIXME check return

        # send token notifications
        cfg = json.loads(urllib2.urlopen("%s/conan_config"%db_url).read())
        conan.email.configure(cfg)
        for addr in addrs:
            token = addrs[addr]['tokens'].itervalues().next()
            conan.email.send_token(addr, addrs[addr]['name'], token)

if __name__ == "__main__":
    main()
