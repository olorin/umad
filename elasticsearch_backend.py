import datetime
from dateutil.tz import *

import elasticsearch

from localconfig import *


es = elasticsearch.Elasticsearch(ELASTICSEARCH_NODES)


def add_to_index(key, value):
	doc_type = determine_doc_type(key)
	index_name = "umad_%s" % doc_type

	# Jam it into a data structure if we're dealing with a bare string
	if type(value) == type('foo'):
		# I'd like to kill this code, log to stderr if we hit this code
		# path and see if we ever hit it. Nuke when it looks safe.
		# -BD@2013-12-18
		import sys
		sys.stderr.write("We got a document that's a string instead "\
				"of a data structure, make it go away.\nThe "\
				"URL is: {0}\n".format(key).encode('utf8') )
		sys.stderr.flush()
		document = { "blob": value }
	else:
		document = value

	# Making use of the local_id hack that shortcuts a way to searching for
	# the "primary key" of a given doc_type
	if "local_id" in document and doc_type != "UNTYPED":
		document[doc_type] = document['local_id']

	# Get the current time in UTC and set `last_indexed` on the document
	document['last_indexed'] = datetime.datetime.now(tzutc())

	# Minimal requirement for the document is that it has a 'blob' key, but ES will support much richer arbitrary schemas
	es.index(
		index = index_name,
		doc_type = doc_type,
		id = key,
		body = document
	)

	return


# Useful for cleaning up mistakes when docs get indexed incorrectly, eg.:
# >>> import elasticsearch_backend
# >>> elasticsearch_backend.delete_from_index('https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=123456')
def delete_from_index(url):
	doc_type = determine_doc_type(url)
	index_name = "umad_%s" % doc_type
	#print "Index type is {0}".format(index_name)

	try:
		es.delete(
			index = index_name,
			doc_type = doc_type,
			id = url
		)
	except elasticsearch.exceptions.NotFoundError as e:
		pass

	# Get rid of it from the legacy index as well
	try:
		es.delete(
			index = "umad",
			doc_type = doc_type,
			id = url
		)
	except elasticsearch.exceptions.NotFoundError as e:
		pass

	return


def search_index(search_term):
	results = es.search(index = ELASTICSEARCH_SEARCH_INDEXES, q = search_term, size=MAX_HITS, df="blob", default_operator="AND")
	hits = results['hits']['hits']

	# XXX: Do sorting and ranking here? Roll it into the search() call


	# A hit looks like this:
	# {
	#     'other_metadata':
	#         {
	#             u'url':      u'https://resources.engineroom.anchor.net.au/resources/8737',
	#             u'customer': u"Barney's colo 7828",
	#             u'blob':     u"complete virtual machine jellyfish misaka squeeze debian barney's colo 7828",
	#             u'name':     u'misaka'
	#         },
	#     'score': 0.095891505000000002,
	#     'id':    u'https://resources.engineroom.anchor.net.au/resources/8737',
	#     'blob':  u"complete virtual machine jellyfish misaka squeeze debian barney's colo 7828"
	# }
	hits = [ {
		'id':             x['_id'],
		'blob':           x['_source']['blob'],
		'score':          x['_score'],
		'other_metadata': [ (y,x['_source'][y]) for y in x['_source'] if y not in ('url','blob') ]
		} for x in hits ]

	return {'hits':hits, 'hit_limit':MAX_HITS}

def get_from_index(url):
	doc_type = determine_doc_type(url)
	index_name = "umad_%s" % doc_type

	args = [index_name, url]
	return es.get(index=index_name, id=url)
