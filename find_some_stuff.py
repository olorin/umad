import sys
import os
import re
import cStringIO
import cgi
from optparse import OptionParser
from colorama import init as init_colorama
from termcolor import colored
from bottle import route, request, response, template, static_file, run

from anchor_riak_connectivity import *


DEBUG = False
def debug(msg):
	if DEBUG:
		sys.stderr.write(str(msg) + '\n')
		sys.stderr.flush()


class response(object):
	def __init__(self):
		self.buffer = cStringIO.StringIO()

	def write(self, data):
		self.buffer.write(data)

	def finalise(self):
		self.value = self.buffer.getvalue()
		self.buffer.close()
		return self.value


def highlight_map(url):
	if url.startswith('https://map.engineroom.anchor.net.au/'):
		return 'highlight-miku'
	if url.startswith('https://rt.engineroom.anchor.net.au/'):
		return 'highlight-luka'
	if url.startswith('https://resources.engineroom.anchor.net.au/'):
		return 'highlight-portal-orange'

	return ''
	return 'highlight-portal-blue'
	return 'highlight-portal-red'



@route('/static/<filename>')
def server_static(filename):
	static_path = os.path.join( os.getcwd(), 'static' )
	return static_file(filename, root=static_path)

@route('/')
def search():
	r = response()
	sys.stdout = r # Hack so you can now use `print` with gay abandon

	template_dict = {}

	q = request.query.q or ''
	q = re.sub(r'([^a-zA-Z0-9"* ])', r'\\\1', q) # Riak barfs on "weird" characters right now, but this escaping seems to work (NB: yes this is fucked http://lzma.so/5VCFKP)
	print >>sys.stderr, "Search term: %s" % q
	template_dict['q_placeholder'] = q

	if not template_dict['q_placeholder']:
		template_dict['q_placeholder'] = "What be ye lookin' for?"

	print """<!DOCTYPE html>
<html>
<head>
	<title>UMAD?</title>
	<link rel="stylesheet" href="/static/umad.css">
</head>

<body>
	<div id="container">
		<div id="searchbox">
			<img src="/static/umad.png" border="0"><br />

			<form name="q" method="get" action="/">
				<p id="searchform">
					<input id="searchinput" name="q" placeholder="%(q_placeholder)s" type="search">
					<input title="Unearth Me A Document!" value="Unearth Me A Document!" accesskey="s" type="submit">
				</p>
			</form>
		</div>""" % template_dict


	if q:
		search_term = q.decode('utf8').encode('ascii', 'ignore')
		(initial_search_term, search_term) = '('+search_term+')', 'blob:' + search_term # turn the search_term into a regex-group for later
		query_re = re.compile(initial_search_term, re.IGNORECASE)


		# Search nao
		results = c.fulltext_search(RIAK_BUCKET, search_term)
		result_docs = results['docs']

		# Clean out cruft, because our index is dirty right now
		result_docs = [ x for x in result_docs if not x['id'].startswith('https://ticket.api.anchor.com.au/') ]
		result_docs = [ x for x in result_docs if not x['id'].startswith('provsys://') ]

		if result_docs:
			print """<div id="results">
			<ul>"""


			for doc in result_docs:
				doc['summary'] = cgi.escape( doc['blob'][:400] )
				doc['summary'] = query_re.sub(r'<strong>\1</strong>', doc['summary'])
				doc['highlight'] = highlight_map(doc['id'])
				print """<li class="%(highlight)s"><a href="%(id)s">%(id)s</a><br />
				%(summary)s
				</li>""" % doc

			print """</ul>
			</div>""" % template_dict
		else:
			print """<div id="results">No results found.</div>"""


	print """
	</div>
</body>
</html>
""" % template_dict

	return r.finalise()


def main(argv=None):
	init_colorama()
	global DEBUG

	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.set_defaults(action=None)
	parser.add_option("--verbose", "-v", dest="debug",     action="store_true", default=False,     help="Log exactly what's happening")
	(options, search_terms) = parser.parse_args(args=argv)

	DEBUG = options.debug

	search_terms[:1] = []
	debug("Your search terms are: ")
	debug(search_terms)

	if not search_terms:
		print "You need to give me a term to search for"
		return 2

	search_term = search_terms[0]

	# Riak doesn't like unicode
	search_term = search_term.decode('utf8').encode('ascii', 'ignore')
	debug( colored("Seaching for '%s'" % search_term, 'green') )

	# Look for substrings in the document blog
	#search_term = 'blob:*' + search_term + '*'
	search_term = 'blob:' + search_term

	# Search nao
	results = c.fulltext_search(RIAK_BUCKET, search_term)
	result_docs = results['docs']


	for doc in result_docs:
		print colored("URL: %s" % doc['id'], 'red')
		print doc['blob'][:400]
		print
	print



	return 0


if __name__ == "__main__":
	run(host='10.108.62.177', port=8080, debug=True)
	#sys.exit(main())

