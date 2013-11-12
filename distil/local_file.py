import sys
from optparse import OptionParser


DEBUG = False
def debug(msg):
	if DEBUG:
		print(msg)


def blobify(filepath):
	if filepath.startswith('file:///'):
		filepath = filepath.replace('file://', '')
	# lol what is error checking?? And sanity in general, for lolhueg files...
	file_contents = open(filepath, 'rb').read()
	return file_contents


def main(argv=None):
	global DEBUG

	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.set_defaults(action=None)
	parser.add_option("--verbose", "-v", dest="debug",     action="store_true", default=False,     help="Log exactly what's happening")
	(options, urls) = parser.parse_args(args=argv)

	DEBUG = options.debug

	urls[:1] = []
	debug(urls)


	for url in urls:
		debug("Going to fetch %s ..." % url)
		content = blobify(url)
		print content


	return 0


if __name__ == "__main__":
	sys.exit(main())

