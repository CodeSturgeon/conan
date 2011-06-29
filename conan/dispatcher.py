#!/usr/bin/env python
import sys
import urllib2
import base64
import traceback
import zipfile
import cStringIO
import json
from conan import gen_token
import conan.email
import datetime

# FIXME this should be arg 1, 2 and 3 (host port db_name) and validated
# FIXME the db name should be taken from the _request_
db_url = 'http://localhost:5984/conan'
statics_id = 'conan_config'
cfg = {}

class BadToken(Exception):
    # Signal there is a serious problem with a token
    pass

class UsedToken(Exception):
    # Signal the token has already beed used
    pass

class NotFound(Exception):
    # Signal a 404
    pass

def requests():
    # Iterator for reading couch requests
    line = sys.stdin.readline()
    while line:
        yield json.loads(line)
        line = sys.stdin.readline()

def load_config():
    # Get config doc from CouchDB
    try:
        cfg_ret = urllib2.urlopen("%s/%s"%(db_url,statics_id))
    except urllib2.HTTPError, e:
        if e.code == 404: sys.exit('cannot find config doc')
        raise e
    return json.loads(cfg_ret.read())

def get_token(token):
    # Get token data, raising errors if there is a problem with the token
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
    # Update token in distribution doc
    iso_now = datetime.datetime.utcnow().isoformat()+'Z'
    tok_doc['addresses'][addr]['tokens'][token]['use_time'] = iso_now
    tok_upd = urllib2.Request("%s/%s"%(db_url,tok_doc['_id']))
    tok_upd.add_data(json.dumps(tok_doc))
    tok_upd.add_header('Content-Type', 'application/json')
    tok_upd.get_method = lambda: 'PUT'
    tok_resp = urllib2.urlopen(tok_upd)

def refresh_token(token):
    # Make a new token based on the old one
    tok_ret = urllib2.urlopen("%s/_design/conan/_view/tokens?key=\"%s\"&include_docs=true"%(db_url,token))
    tok_ret_json = json.loads(tok_ret.read())
    if len(tok_ret_json['rows']) != 1:
        raise BadToken
    if not tok_ret_json['rows'][0]['value'].has_key('use_time'):
        raise BadToken
    # FIXME should check to see if there are unused tokens and error if so

    # Change the distribution doc
    tok_doc = tok_ret_json['rows'][0]['doc']
    iso_now = datetime.datetime.utcnow().isoformat()+'Z'
    token = gen_token()
    addr = tok_ret_json['rows'][0]['value']['address']
    name = tok_doc['addresses'][addr]['name']
    tok_doc['addresses'][addr]['tokens'][token] = {'gen_time': iso_now}
    
    # Update the distribution doc
    tok_upd = urllib2.Request("%s/%s"%(db_url,tok_doc['_id']))
    tok_upd.add_data(json.dumps(tok_doc))
    tok_upd.add_header('Content-Type', 'application/json')
    tok_upd.get_method = lambda: 'PUT'
    tok_resp = urllib2.urlopen(tok_upd)

    # Send email
    conan.email.send_token(addr, name, token)

def compile_zip(doc_id, files):
    # Virtual file for the zip
    zf = cStringIO.StringIO()
    # Zip interface on the virtual file
    z = zipfile.ZipFile(zf, 'w')
    # Compile zip
    for file_name in files:
        # Get file from Couch
        furl = '%s/%s/%s'%(db_url,doc_id,urllib2.quote(file_name))
        try:
            fdata = urllib2.urlopen(furl).read()
        except urllib2.HTTPError, e:
            if e.code == 404: raise BadToken
            raise e
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
    cfg = load_config()
    conan.email.configure(cfg)
    for req in requests():
        if cfg['dispatcher']['reload_config']:
            cfg = load_config()
            conan.email.configure(cfg)
        ret = {'headers': {}}
        try:
            if len(req['path']) < 3:
                # no token supplied
                raise BadToken
            elif len(req['path']) > 3 or req['path'][2].find('.') >= 0:
                # static file
                ctype, b64_data = get_file('/'.join(req['path'][2:]))
            elif req['query'].has_key('request_new'):
                # new token refresh
                token = req['path'][2]
                refresh_token(token)
                ctype, b64_data = get_file('sent_token.html')
            else:
                # token download
                token = req['path'][2]
                tok_doc, addr, pub_id, file_names = get_token(token)
                b64_data = compile_zip(pub_id, file_names)
                use_token(tok_doc, addr, token)
                ctype = 'application/zip'
                c_disp = "attachment; filename=%s.zip" % token
                ret['headers']['Content-Disposition'] = c_disp
            ret['code'] = 200
            ret['headers']['Content-Type'] = ctype
            ret['base64'] = b64_data
        except BadToken:
            ret["code"] = 401
            ctype, b64 = get_file('bad_token.html')
            ret['headers']['Content-Type'] = ctype
            ret['base64'] = b64
        except UsedToken:
            ret["code"] = 403
            ctype, b64 = get_file('used_token.html')
            ret['headers']['Content-Type'] = ctype
            ret['base64'] = b64
        except NotFound:
            ret['code'] = 404
            ctype, b64 = get_file('404.html')
            ret['headers']['Content-Type'] = ctype
            ret['base64'] = b64
        except Exception as e:
            ret["code"] = 500
            if cfg['dispatcher']['allow_debug'] and req['query'].has_key('debug'): 
                body = ''
                #body += "\n%s\n"%e.url
                body += "\n".join(traceback.format_tb(sys.exc_info()[2]))
                body += "\nCFG:\n%s\n" % json.dumps(cfg,indent=2)
                body += "\nREQ:\n%s\n" % json.dumps(req,indent=2)
                ret["body"] = "%s\n\n%s\n"%(e,body)
                ret['headers']['Content-Type'] = 'text/plain'
            else:
                ctype, b64 = get_file('500.html')
                ret['headers']['Content-Type'] = ctype
                ret['base64'] = b64

        sys.stdout.write("%s\n" % json.dumps(ret))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
