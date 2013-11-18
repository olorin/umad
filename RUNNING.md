Distilling and Indexing
=======================

Call `distil_some_stuff.py`, feeding it URLs and file paths.


Config
------

You'll need a `localconfig.py`, this is not supplied in the codebase. It'll
look something like this, just supply whatever variables are relevant for you.

    RIAK_HOST = 'a.b.c.d'
    RIAK_PORT = 8087
    RIAK_BUCKET = 'doc_index'

    ELASTICSEARCH_HOST = 'a.b.c.d'



Searching
=========

UMAD is a simple WSGI app. On an Anchor server:

* Have a user account to host UMAD
* Generate an SSH key, add it as a Deploy Key to the repo on Github
* Setup a virtualenv and install dependencies:
    * riak
    * gunicorn
    * bottle
* Run UMAD with gunicorn (or the WSGI container of your choice)
* Setup nginx to proxy back to UMAD


Ghetto mode
-----------

You can also just use bottle's builtin server, something like this:

    python umad.py -b 192.168.0.1 -p 8080


