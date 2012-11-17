
import urllib2
import uuid
import base64

try:
    import json
except ImportError:
    import simplejson as json

ADD_HEADERS = {'Content-type': 'application/json'}

class JSONRPCException(Exception):
    pass

class Proxy(object):
    def __init__(self, url, namespace=None, username=None, passwd=None,
                pythonic_api=False):
        self._url = url
        self._namespace = namespace
        self._username = username
        self._passwd = passwd
        self._pythonic_api = pythonic_api

    def call(self, fname, *args, **kwargs):
        if self._namespace:
            fname = '%s.%s' % (self._namespace, fname)

        data = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),
            'method': fname,
        }

        if not self._pythonic_api:
            if args and kwargs:
                raise ValueError('You can\'t use positional and keyword '\
                    'arguments together. If you want to, pass '\
                    'pythonic_api=True to the class constructor')
            if args:
                data['params'] = args
            elif kwargs:
                data['params'] = kwargs
        else:
            if args or kwargs:
                data['params'] = (args, kwargs)

        postdata = json.dumps(data)
        req = urllib2.Request(self._url, postdata, ADD_HEADERS)
        if self._username:
            authstr = base64.encodestring(
                '%s:%s' % (self._username, self._passwd))
            authstr = authstr.replace('\n', '')
            req.add_header("Authorization", "Basic %s" % authstr)
        respd = urllib2.urlopen(req).read()
        resp = json.loads(respd)
        if 'error' in resp:
            err = resp.get('error')
            raise JSONRPCException(err.get('message'), err.get('code'))
        else:
            return resp['result']
