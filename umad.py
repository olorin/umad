import sys
import os
import re
import cStringIO
import cgi
from optparse import OptionParser
from bottle import route, request, template, static_file, run, view, default_app

from dateutil.parser import *
from dateutil.tz import *

from elasticsearch_backend import *


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
	#
	# We return a 2-element dict containing a pretty_name and css_class
	if url.startswith('https://map.engineroom.anchor.net.au/'):
		return ('Map',     'highlight-miku')
	if url.startswith('https://rt.engineroom.anchor.net.au/'):
		return ('RT',      'highlight-luka')
	if url.startswith('https://resources.engineroom.anchor.net.au/'):
		return ('Provsys', 'highlight-portal-orange')
	if url.startswith('https://docs.anchor.net.au/'):
		return ('Gollum',  'highlight-portal-blue')

	return ('DEFAULT', '')



@route('/static/<filename>')
def server_static(filename):
	static_path = os.path.join( os.getcwd(), 'static' )
	return static_file(filename, root=static_path)

@route('/')
@view('mainpage')
def search():
	q = request.query.q or ''
	debug("Search term: %s" % q)

	# Fill up a dictionary to pass to the templating engine. It expects the searchterm and a list of document-hits
	template_dict = {}
	template_dict['searchterm'] = q
	template_dict['hits'] = []
	template_dict['hit_limit'] = 0
	template_dict['valid_search_query'] = True
	template_dict['doc_types_present'] = set()


	if q:
		search_term = q
		query_re = re.compile('('+search_term+')', re.IGNORECASE) # turn the search_term into a regex-group for later

		# Pre-query validity check
		template_dict['valid_search_query'] = valid_search_query(search_term)
		if not template_dict['valid_search_query']:
			# Bail out early
			return template_dict

		# Search nao
		results = search_index(search_term)
		result_docs = results['hits']
		template_dict['hit_limit'] = results['hit_limit']

		# Clean out cruft, because our index is dirty right now
		result_docs = [ x for x in result_docs if not x['id'].startswith('https://ticket.api.anchor.com.au/') ]
		result_docs = [ x for x in result_docs if not x['id'].startswith('provsys://') ]

		for doc in result_docs:
			# doc is a dictionary with keys:
			#     blob
			#     id
			first_instance = doc['blob'].find( search_term.strip('"') )
			debug("First instance of %s is at %s" % (search_term, first_instance))

			start_offset = 0
			if first_instance >= 0: # should never fail
				start_offset = max(first_instance-100, 0)

			# The extract *must* be safe for HTML inclusion, as we don't do further escaping later.
			# We want this so we can do searchterm highlighting before passing it to the renderer.
			hit = {}
			hit['id'] = doc['id']
			hit['extract'] = query_re.sub(r'<strong>\1</strong>', cgi.escape(doc['blob'][start_offset:start_offset+400])  )
			# But if we have an excerpt, use that in preference to formatting the blob
			if 'other_metadata' in doc:
				other_metadata = dict(doc['other_metadata'])
				if 'excerpt' in other_metadata:
					hit['extract'] = query_re.sub(r'<strong>\1</strong>', cgi.escape(  other_metadata['excerpt']  )  )
				if 'last_updated' in other_metadata:
					pretty_last_updated = parse(other_metadata['last_updated']).astimezone(tzlocal()).strftime('%Y-%m-%d %H:%M')
					doc['other_metadata'].append( ('last_updated_sydney',pretty_last_updated)  )
			hit['highlight_class'] = highlight_document_source(doc['id'])[1]
			if hit['highlight_class']: # test if not-empty
				template_dict['doc_types_present'].add(highlight_document_source(doc['id']))
			if 'other_metadata' in doc:
				hit['other_metadata'] = doc['other_metadata'] # any other keys that the backend might provide
			else:
				hit['other_metadata'] = []

			# More About Escaping, we have:
			#
			# highlight_class: CSS identifier(?), used as an HTML attribute, please keep this sane and not requiring escaping; let renderer escape it
			# id:              A URL, used as HTML and as an attribute; let renderer escape it
			# extract:         Arbitrary text, used as HTML; we escape it
			# other_metadata:  Arbitrary text, let the renderer escape it

			# Don't display the result if it's a deleted RT ticket.
			sane_meta = dict(hit['other_metadata'])
			if 'rt' in sane_meta and sane_meta.get('status') == 'deleted':
				continue

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

