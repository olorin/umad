import datetime
from dateutil.tz import *

import elasticsearch

from localconfig import *


es = elasticsearch.Elasticsearch(ELASTICSEARCH_NODES)
indices = elasticsearch.client.IndicesClient(es)

class InvalidDocument(Exception): pass


# XXX: This should be cleaned up to take a single argument, the 'document'.
# In all cases, we're called as:
#     add_to_index(doc['url'], doc)
# We should pull out the URL ourselves.
def add_to_index(key, document):
	doc_type = determine_doc_type(key)
	index_name = "umad_%s" % doc_type

	# Sanity check the document. Our minimal requirement for the document
	# is that it has a 'blob' and 'url' key, but ES will support much
	# richer arbitrary fields.
	if 'url' not in document:
		raise InvalidDocument("The document MUST have a 'url' field, cannot add to index: {0}".format(document))
	if 'blob' not in document:
		raise InvalidDocument("The document MUST have a 'blob' field, cannot add to index: {0}".format(document))

	# Allow the user to intuitively specify a doc_type as a search field
	if doc_type != "UNTYPED":
		document[doc_type] = document['blob']

	# Pass the document's type along as extra metadata, for the renderer's
	# benefit.
	document['doc_type'] = doc_type

	# Get the current time in UTC and set `last_indexed` on the document
	document['last_indexed'] = datetime.datetime.now(tzutc())

	es.index(
		index = index_name,
		doc_type = doc_type,
		id = key,
		body = document
	)

	return


# Useful for cleaning up mistakes when docs get indexed incorrectly, eg.:
# >>> import elasticsearch_backend
# >>> elasticsearch_backend.delete_from_index('https://docs.anchor.net.au/some/obsolete/page')
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

	# XXX: nuke this one day
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


def valid_search_query(search_term):
	"Return True/False as to whether the query is valid"
	test_results = indices.validate_query(index=ELASTICSEARCH_SEARCH_INDEXES, q=search_term)
	return test_results[u'valid']

def search_index(search_term, max_hits=MAX_HITS):
	all_hits = []

	# As a temporary local hack, query each index explicitly and perform our own ranking.
	# Goal: Provsys ranks highest, then new gollum docs, then old Map wiki, then RT tickets.
	for backend in KNOWN_DOC_TYPES:
		results = es.search(index="umad_{0}".format(backend), q=search_term, size=max_hits, df="blob", default_operator="AND")
		hits = results['hits']['hits']
		hits = [ {
			'id':             x['_id'],
			'blob':           x['_source']['blob'],
			'score':          x['_score'],
			'other_metadata': [ (y,x['_source'][y]) for y in x['_source'] if y not in ('url','blob') ]
			} for x in hits ]

		all_hits += hits

	return {'hits':all_hits, 'hit_limit':MAX_HITS}


	# A hit looks like this:
	# {
	#     'other_metadata':
	#         {
	#             u'url':      u'http://www.imdb.com/title/tt1319708/',
	#             u'customer': u'Hyron',
	#             u'blob':     u"I didn't ask for this",
	#             u'name':     u'Deus Ex: Human Revolution'
	#         },
	#     'score': 0.095891505000000002,
	#     'id':    u'http://www.imdb.com/title/tt1319708/',
	#     'blob':  u"I didn't ask for this"
	# }


def get_from_index(url):
	doc_type = determine_doc_type(url)
	index_name = "umad_%s" % doc_type

	args = [index_name, url]
	return es.get(index=index_name, id=url)
