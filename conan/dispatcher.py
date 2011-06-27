#!/usr/bin/env python
import sys
import urllib2
import base64
import traceback
import zipfile
import cStringIO

try:
    # Python 2.6
    import json
except:
    # Prior to 2.6 requires simplejson
    import simplejson as json

# FIXME this should be arg 1, 2 and 3 (host port db_name) and validated
db_url = 'http://localhost:5984/conan'
statics_id = 'static_files'

class BadToken(Exception):
    pass

class UsedToken(Exception):
    pass

class NotFound(Exception):
    pass

def requests():
    line = sys.stdin.readline()
    while line:
        yield json.loads(line)
        line = sys.stdin.readline()

def get_token(token):
    tok_ret = urllib2.urlopen("%s/_design/conan/_view/tokens?key=\"%s\"&include_docs=true"%(db_url,token))
    tok_ret_json = json.loads(tok_ret.read())
    if len(tok_ret_json['rows']) != 1:
        raise BadToken
    if tok_ret_json['rows'][0]['value'].has_key('use_time'):
        raise UsedToken
    return (
        tok_ret_json['rows'][0]['doc'],
        tok_ret_json['rows'][0]['value']['address'],
        tok_ret_json['rows'][0]['value']['publication_id'],
        tok_ret_json['rows'][0]['value']['files']
    )

def use_token(tok_doc, addr, token):
    tok_doc['addresses'][addr]['tokens'][token]['use_time'] = 'now'
    tok_upd = urllib2.Request("%s/%s"%(db_url,tok_doc['_id']))
    tok_upd.add_data(json.dumps(tok_doc))
    tok_upd.add_header('Content-Type', 'application/json')
    tok_upd.get_method = lambda: 'PUT'
    tok_resp = urllib2.urlopen(tok_upd)

def compile_zip(doc_id, files):
    # Virtual file for the zip
    zf = cStringIO.StringIO()
    # Zip interface on the virtual file
    z = zipfile.ZipFile(zf, 'w')
    # Compile zip
    for file_name in files:
        # Get file from Couch
        fdata = urllib2.urlopen('%s/%s/%s'%(db_url,doc_id,file_name)).read()
        # Add file to zip
        z.writestr(file_name, fdata)
    # Finish zipping
    z.close()
    # Return base64 of zip file
    return base64.b64encode(zf.getvalue())

def get_file(name):
    try:
        file_ret = urllib2.urlopen("%s/%s/%s"%(db_url,statics_id,name))
    except urllib2.HTTPError, e:
        if e.code == 404: raise NotFound
        raise e
    ctype = file_ret.headers.getheader('Content-Type')
    return ctype, base64.b64encode(file_ret.read())

def main():
    for req in requests():
        ret = {'headers': {}}
        try:
            if len(req['path']) < 3: raise BadToken
            if len(req['path']) > 3 or req['path'][2].find('.') >= 0:
                # static file
                ctype, b64_data = get_file('/'.join(req['path'][2:]))
                ret['headers']['Content-Type'] = ctype
            else:
                # token download
                token = req['path'][2]
                tok_doc, addr, pub_id, file_names = get_token(token)
                b64_data = compile_zip(pub_id, file_names)
                use_token(tok_doc, addr, token)
                ret['headers']['Content-Type'] = 'application/zip'
                ret['headers']['Content-Disposition'] = "attachment; filename=%s.zip"%token
            ret['base64'] = b64_data
            ret['code'] = 200
        except BadToken:
            ret["code"] = 401
            ret["body"] = 'bad'
        except UsedToken:
            ret["code"] = 403
            ret["body"] = 'used'
        except NotFound:
            ret['code'] = 404
            ret['body'] = 'not found'
        except Exception as e:
            trace = "\n".join(traceback.format_tb(sys.exc_info()[2]))
            ret["code"] = 500
            ret["body"] = "%s\n\n%s\n"%(e,trace)
            ret['headers']['Content-Type'] = 'text/plain'
        sys.stdout.write("%s\n" % json.dumps(ret))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
