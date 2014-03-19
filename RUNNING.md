Distilling and Indexing
=======================

Call `distil_some_stuff.py`, feeding it URLs and file paths.


Config
------

You'll need to setup your `localconfig.py`, a live example is included with the
codebase. Define your document types and cluster address suitably.


Searching
=========

UMAD is a simple WSGI app. On an Anchor server:

* Have a user account to host UMAD
* Generate an SSH key, add it as a Deploy Key to the repo on Github
* Setup a virtualenv and install dependencies:
    * gunicorn
    * bottle
* Run UMAD with gunicorn (or the WSGI container of your choice)
* Setup nginx to proxy back to UMAD


Ghetto mode
-----------

You can also just use bottle's builtin server, something like this:

    cd web_frontend; python umad.py -b 192.168.0.1 -p 8080





UMAD Indexer
============

The indexer is composed of multiple components.

1. A listener daemon that receives notifications from systems and stuffs the URL in a Redis database.
2. A worker daemon that pops URLs from the same database and indexes them.

Your distiller plugins may also bring dependencies of their own.


Requirements
------------

You will need the Redis server running somewhere, ideally the same host that's running the indexing daemons.

You will also need some Python libraries:

* Redis bindings (`redis-py`)
* `requests`
* `lxml`
* `provisioningclient`

```
pip install redis requests lxml
```

The provsys distiller will also need the `provisioningclient` library.

```
pip install provisioningclient
```

An interactive script for running one-shot indexing, `distil_some_stuff.py`, is
included. It has a couple of dependencies for enhanced prettiness:

```
pip install colorama termcolor
```
