import sys
import os
from optparse import OptionParser
from colorama import init as init_colorama
from termcolor import colored

import distil
from anchor_riak_connectivity import *


DEBUG = False
def debug(msg):
	if DEBUG:
		sys.stderr.write(str(msg) + '\n')
		sys.stderr.flush()


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
	sys.exit(main())

