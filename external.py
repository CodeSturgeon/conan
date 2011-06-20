#!/usr/bin/env python
import sys
import urllib2
import base64

try:
    # Python 2.6
    import json
except:
    # Prior to 2.6 requires simplejson
    import simplejson as json

def requests():
    # 'for line in sys.stdin' won't work here
    line = sys.stdin.readline()
    while line:
        yield json.loads(line)
        line = sys.stdin.readline()

def respond(code=200, data={}, headers={}):
    #cdata = urllib2.urlopen('http://localhost:5984/conan/testdl/CIMG7610.JPG')
    #b64 = base64.b64encode(cdata.read())
    #headers['Content-Type'] = 'image/jpeg'
    #sys.stdout.write("%s\n" % json.dumps({"code": code, "base64": b64, "headers": headers}))
    sys.stdout.write("%s\n" % json.dumps({
            "code": code,
            "json": data,
            "headers": headers
        }))
    sys.stdout.flush()

def main():
    for req in requests():
        respond(data=req)

if __name__ == "__main__":
    main()
