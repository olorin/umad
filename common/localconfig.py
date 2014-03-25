# Make sure to add your new doc_types to this list as well as to
# `determine_doc_type` below.
KNOWN_DOC_TYPES = [ 'provsys', 'docs', 'map', 'rt', 'customer' ]


# Define this function yourself, remember to add doc_types to the list above.
def determine_doc_type(url):
	if url.startswith('https://map.engineroom.anchor.net.au/'):
		return "map"

	if url.startswith('https://rt.engineroom.anchor.net.au/'):
		return "rt"

	if url.startswith('https://resources.engineroom.anchor.net.au/'):
		return "provsys"

	if url.startswith('https://docs.anchor.net.au/'):
		return "docs"

	if url.startswith('https://customer.api.anchor.com.au/customers/'):
		return "customer"

	# This must return UNTYPED if everything else fails
	# XXX: actually, index names must apparently be lowercase, so this is invalid
	return 'UNTYPED'


# A list of hostnames/IPs and ports, passed straight to the ES constructor.
ELASTICSEARCH_NODES = [ "umad.anchor.net.au:9200" ]


# Not using "_all" because you might have other indices in the ES cluster, or have polluted your indices
ELASTICSEARCH_SEARCH_INDEXES = ','.join( [ "umad_%s" % x for x in KNOWN_DOC_TYPES ] )

# How many hits do you want to display? ES doesn't easily offer pagination, and
# besides, results past the first page probably suck anyway.
MAX_HITS = 50
