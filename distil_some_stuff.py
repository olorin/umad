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
	(options, urls) = parser.parse_args(args=argv)

	DEBUG = options.debug

	urls[:1] = []
	debug("Your input files are: ")
	debug(urls)


	for url in urls:
		if url.startswith('/') and os.path.exists(url):
			url = 'file://' + url
		debug("Going to fetch %s ..." % url)

		try:
			d = distil.Distiller(url)
		except distil.NoUrlHandler:
			print "Don't know how to handle URL: %s" % url
			continue

		debug(colored("-" * len("URL: %s"%url), 'red'))
		debug(colored("URL: %s" % url, 'red'))
		debug(colored("-" * len("URL: %s"%url), 'red'))
		for doc in d.docs:
			debug(colored("Adding to index: %(url)s" % doc, 'green'))
			print doc['blob']
			add_to_index(doc['url'], doc['blob'])
			debug(colored("Success!", 'green'))
			print


	return 0


if __name__ == "__main__":
	sys.exit(main())

