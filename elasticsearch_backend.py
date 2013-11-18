import elasticsearch

from localconfig import *


es = elasticsearch.Elasticsearch(ELASTICSEARCH_NODES)


def add_to_index(key, value):
	if key.startswith('https://map.engineroom.anchor.net.au/'):
		doc_type = "moin_map"
	elif key.startswith('https://rt.engineroom.anchor.net.au/'):
		doc_type = "rt"
        elif key.startswith('https://resources.engineroom.anchor.net.au/'):
		doc_type = "provsys"
	else:
		doc_type = "other"

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


def search_index(search_term):
	querydoc = {"query": {"match": {"blob": search_term}}}

	results = es.search(index = ELASTICSEARCH_INDEX, body = querydoc)
	hits = results['hits']['hits']

	# XXX: Do sorting and ranking here?

	# A hit looks like this:
	# {'other_metadata': {u'url': u'https://resources.engineroom.anchor.net.au/resources/8737', u'customer': u"Barney's colo 7828", u'blob': u"complete virtual machine jellyfish misaka squeeze debian barney's colo 7828", u'name': u'misaka'}, 'score': 0.095891505000000002, 'id': u'https://resources.engineroom.anchor.net.au/resources/8737', 'blob': u"complete virtual machine jellyfish misaka squeeze debian barney's colo 7828"}
	hits = [ {'id': x['_id'], 'blob': x['_source']['blob'], 'score':x['_score'], 'other_metadata':  [ (y,x['_source'][y]) for y in x['_source'] if y not in ('url','blob') ]  } for x in hits ]

	return hits
