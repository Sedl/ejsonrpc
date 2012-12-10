ejsonrpc
========

Enhanced JSONRPC WSGI server and client

Features
--------
* JSONRPC v2.0
* HTTP Basic Auth
* Namespaces
* Pythonic function calls. Uses \*args and \*\*kwargs as parameters if you want to, and therefore more flexible for python users.

Planned features
----------------
* Py3k support

Not yet implemented
-------------------
* Batch calls

Debian Packaging
----------------
To build a debian package, install stdeb (pip install stdeb) and run python `setup.py --command-packages=stdeb.command bdist_deb`
