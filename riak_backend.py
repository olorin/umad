from riak import RiakClient

from localconfig import *


c = RiakClient(host=RIAK_HOST, pb_port=RIAK_PORT, protocol='pbc')

index = c.bucket(RIAK_BUCKET)
index.enable_search()

def add_to_index(key, value):
	# Our Riak processor is dumb right now, only uses the blob key of the document.
	value = value['blob']

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


def search_index(search_term):
	search_term = 'blob:' + search_term # We assume the search term has been cleaned up to ascii-only already

	results = c.fulltext_search(RIAK_BUCKET, search_term)
	result_docs = results['docs']

	return result_docs
