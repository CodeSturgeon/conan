#!/usr/bin/env python
import sys
import urllib2
import base64
import traceback

try:
    # Python 2.6
    import json
except:
    # Prior to 2.6 requires simplejson
    import simplejson as json


class BadToken:
    pass

class UsedToken:
    pass

def requests():
    # 'for line in sys.stdin' won't work here
    line = sys.stdin.readline()
    while line:
        yield json.loads(line)
        line = sys.stdin.readline()

def use_token(token):
    tok_ret = urllib2.urlopen("http://localhost:5984/conan/_design/conan/_view/tokens?key=\"%s\"&include_docs=true"%token)
    tok_ret_json = json.loads(tok_ret.read())
    if len(tok_ret_json['rows']) != 1:
        raise BadToken
    # FIXME if 404 then raise BadToken
    tok_doc = tok_ret_json['rows'][0]['doc']
    if tok_doc['tokens'][token]['use_time'] != '':
        raise UsedToken
    tok_doc['tokens'][token]['use_time'] = 'now'
    tok_upd = urllib2.Request("http://localhost:5984/conan/%s"%tok_doc['_id'])
    tok_upd.add_data(json.dumps(tok_doc))
    tok_upd.add_header('Content-Type', 'application/json')
    tok_upd.get_method = lambda: 'PUT'
    tok_resp = urllib2.urlopen(tok_upd)
    return tok_doc['_id'], tok_doc['tokens'][token]['file_name']

def give_file(doc_id, file_name):
    cdata = urllib2.urlopen('http://localhost:5984/conan/%s/%s'%(doc_id,file_name))
    b64 = base64.b64encode(cdata.read())
    headers = {}
    headers['Content-Type'] = cdata.headers.getheader('Content-Type')
    sys.stdout.write("%s\n" % json.dumps({"code": 200, "base64": b64, "headers": headers}))
    sys.stdout.flush()

def main():
    for req in requests():
        try:
            token = req['path'][2] # FIXME fails as a 500
            doc_id, file_name = use_token(token)
            give_file(doc_id, file_name)
        except BadToken:
            sys.stdout.write("%s\n" % json.dumps({"code": 401, "body": 'bad'}))
            sys.stdout.flush()
        except UsedToken:
            sys.stdout.write("%s\n" % json.dumps({"code": 403, "body": 'used'}))
            sys.stdout.flush()
        except Exception as e:
            trace = "\n".join(traceback.format_tb(sys.exc_info()[2]))
            sys.stdout.write("%s\n" % json.dumps({"code": 500, "body": "%s\n\n%s\n"%(e,trace), 'headers': {'Content-Type': 'text/plain'} }))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
