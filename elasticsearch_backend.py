import elasticsearch

from localconfig import *


es = elasticsearch.Elasticsearch(ELASTICSEARCH_NODES)


def determine_doc_type(url):
	if url.startswith('https://map.engineroom.anchor.net.au/'):
		return "moin_map"
	if url.startswith('https://rt.engineroom.anchor.net.au/'):
		return "rt"
        if url.startswith('https://resources.engineroom.anchor.net.au/'):
		return "provsys"

	return "other"


def add_to_index(key, value):
	doc_type = determine_doc_type(key)

	if type(value) == type('foo'):
		# Process the string into a data structure
		document = {
			"blob": value,
		}
	else:
		document = value

	# Minimal requirement for the document is that it has a 'blob' key, but ES will support much richer arbitrary schemas
	es.index(
		index = ELASTICSEARCH_INDEX,
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

	es.delete(
		index = ELASTICSEARCH_INDEX,
		doc_type = doc_type,
		id = url
	)

	return


def search_index(search_term):
	# This doesn't work as well as passing search terms directly through lol
	#querydoc = {"query": {"match": {"blob": search_term}}}
	#results = es.search(index = ELASTICSEARCH_INDEX, body = querydoc)

	results = es.search(index = ELASTICSEARCH_INDEX, q = search_term)
	hits = results['hits']['hits']

	# XXX: Do sorting and ranking here?

	# A hit looks like this:
	# {'other_metadata': {u'url': u'https://resources.engineroom.anchor.net.au/resources/8737', u'customer': u"Barney's colo 7828", u'blob': u"complete virtual machine jellyfish misaka squeeze debian barney's colo 7828", u'name': u'misaka'}, 'score': 0.095891505000000002, 'id': u'https://resources.engineroom.anchor.net.au/resources/8737', 'blob': u"complete virtual machine jellyfish misaka squeeze debian barney's colo 7828"}
	hits = [ {'id': x['_id'], 'blob': x['_source']['blob'], 'score':x['_score'], 'other_metadata':  [ (y,x['_source'][y]) for y in x['_source'] if y not in ('url','blob') ]  } for x in hits ]

	return hits
