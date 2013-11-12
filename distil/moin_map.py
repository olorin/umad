import sys
import os
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests
from optparse import OptionParser

CA_CERT_PATH = 'AnchorCA.pem'
RAGEWIKI_USER = os.environ.get('RAGEWIKI_USER', '')
RAGEWIKI_PASS = os.environ.get('RAGEWIKI_PASS', '')


DEBUG = False
def debug(msg):
	if DEBUG:
		print(msg)


def tidy_url(url):
	"This is an awful hack that might destroy query parameters"
	url = url.partition('#')[0]
	urlparts = url.partition('?')
	if urlparts[2]: # We have query terms
		return '&'.join([ urlparts[0]+'?action=raw', urlparts[2] ])
	else: # No query terms
		return urlparts[0]+'?action=raw'

def fetch(url):
	global RAGEWIKI_USER
	global RAGEWIKI_PASS
	url = tidy_url(url)
	debug("Using moin handler to fetch %s ..." % url)
	return requests.get(url, auth=(RAGEWIKI_USER, RAGEWIKI_PASS), verify=CA_CERT_PATH)

def blobify(url):
	response = fetch(url)
	return response.content


def main(argv=None):
	global DEBUG
	global RAGEWIKI_USER
	global RAGEWIKI_PASS

	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.set_defaults(action=None)
	parser.add_option("--verbose", "-v", dest="debug",     action="store_true", default=False,     help="Log exactly what's happening")
	parser.add_option("--user",    "-u", dest="http_user",                      default=RAGEWIKI_USER, help="The username to auth with against the wiki")
	parser.add_option("--pass",    "-p", dest="http_pass",                      default=RAGEWIKI_PASS, help="The password to auth with against the wiki")
	(options, urls) = parser.parse_args(args=argv)

	DEBUG = options.debug
	RAGEWIKI_USER = options.http_user
	RAGEWIKI_PASS = options.http_pass

	debug(options)
	urls[:1] = []
	debug(urls)


	for url in urls:
		debug("Going to fetch %s ..." % url)

		r = fetch(url)
		print r.content


	return 0


if __name__ == "__main__":
	sys.exit(main())

