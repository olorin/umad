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
	# {u'_score': 0.25, u'_type': u'provsys', u'_id': u'https://resources.engineroom.anchor.net.au/resources/6222', u'_source': {u'blob': u'complete virtual machine parley ocean170 lenny debian strategysteps pty ltd 11946'}, u'_index': u'umad'}
	hits = [ {'id': x['_id'], 'blob': x['_source']['blob'] } for x in hits ]

	return hits
