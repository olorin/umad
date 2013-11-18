import sys
import os
import re
import cStringIO
import cgi
from optparse import OptionParser
from bottle import route, request, template, static_file, run, view, default_app

from anchor_riak_connectivity import *


DEBUG = False
def debug(msg, force_debug=False):
	if DEBUG or force_debug:
		sys.stderr.write(str(msg) + '\n')
		sys.stderr.flush()


def highlight_document_source(url):
	# Valid values are kept in umad.css
	# - highlight-miku
	# - highlight-luka
	# - highlight-portal-orange
	# - highlight-portal-blue
	# - highlight-red
	if url.startswith('https://map.engineroom.anchor.net.au/'):
		return 'highlight-miku'
	if url.startswith('https://rt.engineroom.anchor.net.au/'):
		return 'highlight-luka'
	if url.startswith('https://resources.engineroom.anchor.net.au/'):
		return 'highlight-portal-orange'

	return ''



@route('/static/<filename>')
def server_static(filename):
	static_path = os.path.join( os.getcwd(), 'static' )
	return static_file(filename, root=static_path)

@route('/')
@view('mainpage')
def search():
	q = request.query.q or ''
	q = re.sub(r'([^a-zA-Z0-9"* ])', r'\\\1', q) # Riak barfs on "weird" characters right now, but this escaping seems to work (NB: yes this is fucked http://lzma.so/5VCFKP)
	debug("Search term: %s" % q)

	# Fill up a dictionary to pass to the templating engine. It expects the searchterm and a list of document-hits
	template_dict = {}
	template_dict['searchterm'] = q
	template_dict['hits'] = []


	if q:
		search_term = q.decode('utf8').encode('ascii', 'ignore')
		(initial_search_term, search_term) = search_term, 'blob:' + search_term # turn the search_term into a regex-group for later
		query_re = re.compile('('+initial_search_term+')', re.IGNORECASE)

		# Search nao
		results = c.fulltext_search(RIAK_BUCKET, search_term)
		result_docs = results['docs']

		# Clean out cruft, because our index is dirty right now
		result_docs = [ x for x in result_docs if not x['id'].startswith('https://ticket.api.anchor.com.au/') ]
		result_docs = [ x for x in result_docs if not x['id'].startswith('provsys://') ]

		for doc in result_docs:
			first_instance = doc['blob'].find( initial_search_term.strip('"') )
			print >>sys.stderr, "First instance of %s is at %s" % (initial_search_term, first_instance)

			start_offset = 0
			if first_instance >= 0: # should never fail
				start_offset = max(first_instance-100, 0)

			# The extract *must* be safe for HTML inclusion, as we don't do further escaping later.
			# We want this so we can do searchterm highlighting before passing it to the renderer.
			hit = {}
			hit['id'] = doc['id']
			hit['extract'] = query_re.sub(r'<strong>\1</strong>', cgi.escape(doc['blob'][start_offset:start_offset+400])  )
			hit['highlight_class'] = highlight_document_source(doc['id'])

			# More About Escaping, we have:
			#
			# highlight_class: CSS identifier(?), used as an HTML attribute, please keep this sane and not requiring escaping; let renderer escape it
			# id:              A URL, used as HTML and as an attribute; let renderer escape it
			# extract:         Arbitrary text, used as HTML; we escape it

			template_dict['hits'].append(hit)

	return template_dict


# For encapsulating in a WSGI container
application = default_app()


def main(argv=None):
	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.add_option("--verbose", "-v", dest="debug", action="store_true", default=False,       help="Log exactly what's happening")
	parser.add_option("--bind", "-b",    dest="bind_host",                  default='localhost', help="Hostname/IP to listen on, [default: %default]")
	parser.add_option("--port", "-p",    dest="bind_port", type="int",      default=8080,        help="Port number to listen on, [default: %default]")
	(options, search_terms) = parser.parse_args(args=argv)

	global DEBUG
	DEBUG = options.debug

	run(host=options.bind_host, port=options.bind_port, debug=True)

	return 0

if __name__ == "__main__":
	sys.exit(main())

