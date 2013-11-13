UMAD's data vampirism is modular, you write distillation modules that take a URL and return a blob to be indexed.

Interface
=========

The interface is super simple:

* You provide a callable named `blobify`
* It's called with a single argument, a URL to the thing/s to be indexed. This is opaque and may have a bogus schema and everything. This is your problem for now.
* Your callable returns an iterable of blobs to be indexed.
* Blobs are a dictionary with two keys, a `url` and a `blob`. Because the canonical URL for a document may be different from what you provided, the distiller can clean it up for you. The blob is plain ascii text.


Hello World distiller
=====================

1. Create your module in the `distil/` directory, we're calling it `helloworld.py`

      import sys
      import foo
      import bambleweenie

      def blobify(url):
          result = {}
          result['url'] = "hello://adam.jensen/greeting"
          result['blob'] = "I didn't ask for this"
          return [result]

2. You need to hook your module into the framework, add yourself to `__init__.py`

      # At the top
      import helloworld

      # And in the URL-matching messiness
      ...
      elif url.startswith('hello://'):
          self.fetcher = helloworld


