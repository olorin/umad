import sys
import os
from optparse import OptionParser
from colorama import init as init_colorama
from termcolor import colored

import distil
from elasticsearch_backend import *


DEBUG = True
def debug(msg):
	if DEBUG:
		if type(msg) is unicode:
			msg = msg.encode('utf8')
		sys.stderr.write(msg)
		sys.stderr.write('\n')
		sys.stderr.flush()

def red(msg):
	return colored(msg, 'red')
def green(msg):
	return colored(msg, 'green')
def blue(msg):
	return colored(msg, 'blue')


def main(argv=None):
	init_colorama()
	global DEBUG

	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.set_defaults(action=None)
	parser.add_option("--quiet", "-q", dest="debug", action="store_false", default=True, help="Suppress nice human-readable reporting")
	(options, urls) = parser.parse_args(args=argv)

	DEBUG = options.debug

	urls[:1] = []
	debug("Your input files are: ")
	for url in urls:
		debug("\t%s" % url)


	for url in urls:
		if url.startswith('/') and os.path.exists(url):
			url = 'file://' + url
		debug(red("-" * len("URL: %s"%url)))
		debug(red("URL: %s" % url))
		debug(red("-" * len("URL: %s"%url)))

		try:
			d = distil.Distiller(url)
		except distil.NoUrlHandler:
			print "Don't know how to handle URL: %s" % url
			continue

		for doc in d.docs:
			if doc is None:
				continue
			debug(green("Adding to index: %(url)s" % doc))

			# Depending on the backend, the blob will either be str
			# or unicode:
			#   Gollum:  unicode
			#   RT:      str
			#   Map:     str
			#   Provsys: str
			#
			# We need to test for this because blindly encode()ing
			# the blob will result in errors if it's already a
			# UTF8 str.
			trimmed_blob = doc['blob'][:400]
			if type(trimmed_blob) is str:
				debug(blue("400 chars of blob: {0}".format(trimmed_blob)))
			else: # unicode
				debug(blue(u"400 chars of blob: {0}".format(trimmed_blob)))
			add_to_index(doc['url'], doc)
			debug(green("Success!"))
			debug("")

			debug(red("-------"))
			debug(red("Now reprinting the document we just indexed"))
			document_just_added = get_from_index(doc['url'])['_source']
			for key in sorted(document_just_added):
				if not isinstance(document_just_added[key], (str,unicode)):
					document_just_added[key] = str(document_just_added[key])
				debug(green(key.capitalize()))
				debug(u"\t{0}".format(document_just_added[key][:1000]).encode('utf8'))
			debug("")


	return 0


if __name__ == "__main__":
	sys.exit(main())

