from riak import RiakClient
import time

RIAK_HOST = '110.173.154.175'
RIAK_PORT = 8087
RIAK_BUCKET = 'doc_index'

c = RiakClient(host=RIAK_HOST, pb_port=RIAK_PORT, protocol='pbc')

index = c.bucket(RIAK_BUCKET)
index.enable_search()

def debug(msg):
	import sys
	sys.stderr.write(msg + '\n')
	sys.stderr.flush()

def add_to_index(key, value):
	# Mangle the data to ascii, dropping any non-ascii characters.  We may
	# work around this in future by indexing urlencoded documents, though
	# it'll mean that all queries need to be urlencoded as well. Daft by
	# maybe workable.
	# https://github.com/basho/riak-python-client/issues/32
	if type(value) != type(u''): # Python barfs if you try to decode a string that's already Unicode
		value = value.decode('utf8', 'ignore')
	value = value.encode('ascii', 'ignore')

	# Riak wants your values to be iterable structures (JSON docs)? Okay.
	value = { 'blob': value }

	blob = index.new(key, value)
	c.fulltext_add(RIAK_BUCKET, [ blob.data  ])
	blob.store()
	return blob

