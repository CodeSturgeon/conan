import urllib2
import json

from_addr = 'no-reply@raybeam.com'
pma_key = ''
token_base = 'http://localhost:5984/conan/_tokened_download/'

def send_token(addr, name, token):
    msg = {
        'To': addr,
        'From': from_addr,
        'Subject': 'New download available',
        'TextBody': "Your download is available here:\n"+token_base+token
    }

    mail_req = urllib2.Request('http://api.postmarkapp.com/email')
    mail_req.add_header('Content-Type', 'application/json')
    mail_req.add_header('X-Postmark-Server-Token', pma_key)
    mail_req.add_data(json.dumps(msg))
    mail_ret = urllib2.urlopen(mail_req)
    return mail_ret
