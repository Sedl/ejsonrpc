#!/usr/bin/env python

from ejsonrpc import Proxy
import time

if __name__ == '__main__':
    # Authentication is done with HTTP Basic auth
    client = Proxy(
        'http://localhost:8080/',
        namespace='hello',
        username='test1',
        passwd='test2',
        pythonic_api=True
    )
    print client.call('hello', 'sepp')
