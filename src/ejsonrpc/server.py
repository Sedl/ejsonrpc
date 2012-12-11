
import traceback
import sys
import base64


try:
    import json
except ImportError:
    import simplejson as json

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
INVALID_NAMESPACE = -32000
UNKNOWN_NAMESPACE = -32001
PYTHON_EXCEPTION = -32002

ERRORS = {
    PARSE_ERROR:  'Parse Error',
    INVALID_REQUEST: 'Invalid Request',
    METHOD_NOT_FOUND: 'Method Not Found',
    INVALID_PARAMS: 'Invalid Params',
    INTERNAL_ERROR: 'Internal Error',
    # own errors
    INVALID_NAMESPACE: 'No Or Invalid Namespace',
    UNKNOWN_NAMESPACE: 'Unknown Namespace',
    PYTHON_EXCEPTION: 'Unknown Python Exception'
}

def ignore(fn):
    fn.jsonrpc_ignore = True
    return fn

class RPCException(Exception):
    def __init__(self, callid, errcode, message=None):
        self.callid = callid
        self.errcode = errcode
        self._message = message

    @property
    def message(self):
        if self._message:
            return self._message
        return ERRORS[self.errcode]

    def as_dict(self):
        res = {
            'jsonrpc': '2.0',
            'id': self.callid,
            'error': {
                'code': self.errcode,
                'message': self.message,
            }
        }
        return res

class JSONApp(object):
    def __init__(self, pythonic_api=False, auth_cb=None):
        self._pythonic_api = pythonic_api
        self._namespaces = {}
        self._auth_cb = auth_cb


    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] != "POST":
            start_response(
                '405 Method Not Allowed',
                [('Content-type', 'text/plain')]
            )
            return ['405 Method Not Allowed']

        if not environ['CONTENT_TYPE'] == 'application/json':
            start_response('400 Bad Request',
                    [('Content-type', 'text/plain')])
            return ["Content-type must be application/json"]

        if self._auth_cb:
            remoteaddr = environ['REMOTE_ADDR']
            if 'HTTP_AUTHORIZATION' in environ:
                authstr = environ['HTTP_AUTHORIZATION']
                if not authstr.startswith('Basic '):
                    start_response('401 Unauthorized',
                        [('Content-type', 'text/plain')])
                    return ['Unknown authorization method']
                username, pwd = base64.b64decode(authstr[5:]).split(':', 1)

            else:
                username = None
                pwd = None

            if not self._auth_cb(remoteaddr, username, pwd):
                start_response('401 Unauthorized',
                    [('Content-type', 'text/plain')])
                return ['Authorization failed']

        if 'CONTENT_LENGTH' in environ:
            clen = int(environ['CONTENT_LENGTH'])
        else:
            clen = -1

        data = environ['wsgi.input'].read(clen)
        try:
            dec = json.loads(data)
            resdata = self.dispatch(dec)
        except ValueError:
            resdata = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {
                    'code':PARSE_ERROR,
                    'message': ERRORS[PARSE_ERROR]
                }
            }
        except RPCException, exc:
            resdata = exc.as_dict()

        start_response(
            '200 OK',
            [('Content-type', 'application/json')]
        )
        if resdata:
            return [json.dumps(resdata)]
        return []


    def _getparams(self, jsondata):
        params = jsondata.get('params', None)

        if not params:
            return (list(), dict())

        if not type(params) in (list, dict):
            raise RPCException(jsondata.get('id', None), INVALID_PARAMS)

        if self._pythonic_api:
            if not len(params) == 2:
                raise RPCException(jsondata.get('id', None), INVALID_PARAMS)

            if not isinstance(params[0], list):
                raise RPCException(jsondata.get('id', None), INVALID_PARAMS)

            if not isinstance(params[1], dict):
                raise RPCException(jsondata.get('id', None), INVALID_PARAMS)

            return tuple(params)

        else:

            if isinstance(params, list):
                return (params, dict())
            elif isinstance(params, dict):
                return (list(), params)
            else:
                raise RPCException(jsondata.get('id', None), INVALID_PARAMS)

    def dispatch(self, jsondata):
        call_id = jsondata.get('id', None)

        if not jsondata.get('jsonrpc') == '2.0':
            raise RPCException(call_id, INVALID_REQUEST)


        if not 'method' in jsondata:
            raise RPCException(call_id, INVALID_REQUEST)

        # TODO: Support batch calls

        try:
            namesp, method = jsondata.get('method').split('.', 1)
        except ValueError:
            raise RPCException(call_id, INVALID_NAMESPACE)

        if not namesp:
            raise RPCException(call_id, INVALID_NAMESPACE)

        if not namesp in self._namespaces:
            raise RPCException(call_id, UNKNOWN_NAMESPACE)

        if method.startswith('_'):
            raise RPCException(call_id, METHOD_NOT_FOUND)

        func = getattr(self._namespaces[namesp], method, None)

        if func is None:
            raise RPCException(call_id, METHOD_NOT_FOUND)

        if getattr(func, 'jsonrpc_ignore', False):
            raise RPCException(call_id, METHOD_NOT_FOUND)

        args, kwargs = self._getparams(jsondata)

        try:
            fres = func(*args, **kwargs)
        except Exception, exc:
            tbl = traceback.format_exception(*sys.exc_info())
            msg = ''.join(tbl)
            raise RPCException(call_id, PYTHON_EXCEPTION, msg)

        if call_id:
            # Only return result if an id was given.
            # Calls without an id are notifications and should not return
            # anything
            res = {
                'jsonrpc': '2.0',
                'result': fres,
                'id': call_id
            }
            return res

    # dict emulation
    def __getitem__(self, key):
        return self._namespaces[key]

    def __setitem__(self, key, val):
        self._namespaces[key] = val

    def items(self):
        return self._namespaces.items()

    def keys(self):
        return self._namespaces.keys()

