
import os
import sys
from urllib import unquote_plus


def get_multipart(data):
    '''
    This method *MUST* be run with unbuffered input!
    python -u
    '''
    content_type = parse_semi(env['CONTENT_TYPE'])
    
    boundary = '--'+content_type['boundary']
    
    print 'BOUNDARY =',boundary
    
    string = data
    if not string.startswith(boundary):
        raise ValueError('form-data boundary does not match')
        
    class part(str):
        pass
        
    def make_part(string):
        headers     = {}
        disposition = {}
        data    = ''
        
        while 1:
            n = string.find('\r\n')
            if n == -1:
                raise ValueError('unexpected EOF while parsing form part')
            if n == 0:
                string = string[2:-2]
                break
            header, value = string[:n].split(': ', 1)
            headers[header] = value
            string = string[n+2:]
        data        = part(string)
        disposition = parse_semi(headers['Content-Disposition'])
        name = disposition.pop('name')
        for n, v in disposition.items():
            setattr(data, n, v)
        return name, data
        
    string  = data[len(boundary+'\r\n'):]
    parts   = {}
    while 1:
        print '<pre>'+string+'</pre>'
        n = string.find(boundary)
        if n == -1:
            raise ValueError('unexpected EOF while parsing form-data (ATTN: make sure this script is running with unbuffered stdin, as the default (text-mode on windows) will fail when reading certain non-text characters) (#python -u for unbuffered stdin/out)')
        name, value = make_part(string[:n])
        parts[name] = value
        if string[n:-2] == boundary+'--':
            break
        string = string[len(boundary)+n+2:]
    return parts

def parse_semi(string):
    d = {}
    for i in string.split('; '):
        try:
            k, v = i.split('=',1)
        except ValueError:
            k, v = '', i
        d[k] = v
    return d

def parse_query(string):
    d = {}
    string = string.split('&')
    for i in string:
        try:
            key, value = i.split('=', 1)
        except ValueError:
            key, value = i, ''
        d[key] = unquote_plus(value)
    return d

def get_post(data):
    if not env['REQUEST_METHOD'] == 'POST':
        return {}
    if env['CONTENT_TYPE'].startswith('multipart/form-data'):
        return get_multipart(data)
    if env['CONTENT_TYPE'].startswith('application/x-www-form-urlencoded'):
        return parse_query(data)

def get_cookie():
    if 'HTTP_COOKIE' not in env:
        return {}
    return parse_semi(env['HTTP_COOKIE'])
    

env = os.environ

localfile = env.get('SCRIPT_FILENAME','')
localroot = env.get('DOCUMENT_ROOT','')

server = env.get('SERVER_NAME')
if env.get('SERVER_PORT') and env.get('SERVER_PORT') != '80':
    server += ':' + env.get('SERVER_PORT')
    
assert localfile.startswith(localroot)
urlroot = '/'
urlfile = localfile[len(localroot):]
    
fullurlroot = 'http://%s' % server
fullurlfile = fullurlroot + urlfile

data = sys.stdin.read()

get     = parse_query(env.get('QUERY_STRING',''))
post    = ''#get_post(data)

if 'PATH_INFO' in env:
    info = env['PATH_INFO'].split('/')[1:]
else:
    info = []
    
infop = '/'.join(info)

# browser information


is_internetexplorer6 = ('MSIE 6.0' in env.get('HTTP_USER_AGENT', ''))
is_internetexplorer7 = ('MSIE 7.0' in env.get('HTTP_USER_AGENT', ''))
                      
is_internetexplorer = is_internetexplorer6 or is_internetexplorer7



# safari2 Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/XX (KHTML, like Gecko) Safari/YY
# safari3 Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/XX (KHTML, like Gecko) Version/ZZ Safari/YY

is_safari = 'AppleWebKit' in env.get('HTTP_USER_AGENT', '')
is_safari2 = is_safari and not 'Version' in env.get('HTTP_USER_AGENT', '')
is_safari3 = is_safari and     'Version' in env.get('HTTP_USER_AGENT', '')


def path(*args):
    p = os.path.dirname(env['SCRIPT_NAME'])
    if p == '/': p = ''
    return os.path.join(*([p] + list(args))).replace('\\','/')
    
def fpath(*args):
    p = env['SCRIPT_NAME']
    return os.path.join(*([p] + list(args))).replace('\\','/')

