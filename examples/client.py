#!/usr/bin/env python

from ejsonrpc import Proxy
import time

if __name__ == '__main__':
    client = Proxy('http://localhost:8080/', namespace='hello', pythonic_api=True)
    print client.call('hello', 'sepp')
