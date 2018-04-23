# kevinlynx@gmail.com
import datetime, os
import urllib2, urllib, httplib, socket
from HTMLParser import HTMLParser

def _p(s):
    print(s.encode('GBK', 'ignore'))

def read_file_string(file):
    try:
        with open(file, 'r') as fp:
            s = fp.read()
            return s
    except IOError, e:
        return ''

def write_bfile(name, data):
    with open(name, 'wb') as fp:
        fp.write(data)

def read_bfile(name):
    with open(name, 'rb') as fp:
        return fp.read()

def ensure_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError, e:
        if e.errno != os.errno.EEXIST:
            raise

def safe_remove_file(file):
    try:
        os.remove(file)
    except OSError, e:
        pass

def http_get(url, d_params = {}, timeout = 3):
    return http_req(url, timeout, d_params)

def http_post(url, timeout = 3, body = None, d_params = {}, headers = {}):
    return http_req(url, timeout, d_params, body, headers)

def http_req(url, timeout, d_params = {}, body = None, headers = {}):
    if len(d_params) > 0:
        q = urllib.urlencode(d_params)
        url = url + '?' + q
    content = ''
    try:
        request = urllib2.Request(url, body, headers)
        response = urllib2.urlopen(request, timeout = timeout)
        content = response.read() 
    except urllib2.HTTPError, e:
        pass
    except urllib2.URLError, e:
        print('request %s failed: %r' % (url, e))
    except socket.timeout, e:
        print('request %s failed, socket timeout %r' % (url, e))
    return content

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def as_datetime(t):
    if type(t) == long or type(t) == int:
        t = datetime.datetime.fromtimestamp(t / 1000)
    if not t: 
        t = datetime.datetime.fromtimestamp(0)
    return t

if __name__ == '__main__':
    write_bfile('x.jpg', http_get('http://www.52bama.cn/yongpin/uploads/allimg/160416/213HJ518-0.jpg'))


