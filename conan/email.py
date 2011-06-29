import urllib2
import json

cfg = {}

def configure(newcfg):
    # Yes... it's sloppy, but it works for now
    global cfg
    cfg = newcfg

def send_token(addr, name, token):
    global cfg
    # FIXME need to sanitize template output (XSS, \n, stuff like that)
    template_vars = {'token': token, 'name': name}
    text = cfg['email']['text_template']%template_vars
    html = cfg['email']['html_template']%template_vars
    subject = cfg['email']['subject_template']%template_vars
    msg = {
        'To': addr,
        'From': cfg['email']['from_addr'],
        'Subject': subject,
        'TextBody': text,
        'HtmlBody': html
    }

    mail_req = urllib2.Request('http://api.postmarkapp.com/email')
    mail_req.add_header('Content-Type', 'application/json')
    mail_req.add_header('X-Postmark-Server-Token', cfg['email']['pma_key'])
    mail_req.add_data(json.dumps(msg))
    mail_ret = urllib2.urlopen(mail_req)
    return mail_ret
