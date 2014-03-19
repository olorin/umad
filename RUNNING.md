Distilling and Indexing
=======================

Call `distil_some_stuff.py`, feeding it URLs and file paths.


Config
------

You'll need a `localconfig.py`, this is not supplied in the codebase. It'll
look something like this, just supply whatever variables are relevant for you.

    ELASTICSEARCH_NODES = [ "your.fqdn.here:9200" ]
    MAX_HITS = 50




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

The indexer is composed of two components.

1. A listener daemon that receives notifications from systems and stuffs the URL in a Redis database.
2. A worker daemon that pops URLs from the same database and indexes them.

Requirements
------------

You will need the Redis server running somewhere, ideally the same host that's running the indexing daemons.

You will also need some Python libraries:

* Redis bindings (`redis-py`)
* `requests`
* `lxml`
* `provisioningclient`

