#!/usr/bin/env python

# Small external that just dumps the params it was passed

import sys

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
