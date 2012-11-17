#!/usr/bin/env python

from wsgiref.simple_server import make_server

from ejsonrpc import JSONApp


if __name__ == '__main__':
    class Hello:
        def hello(self, name='world'):
            return 'Servus %s!' % name

    app = JSONApp(pythonic_api=True)
    app['hello'] = Hello()
    srv = make_server('localhost', 8080, app)
    srv.serve_forever()
