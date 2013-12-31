import sys
import os
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests


def tidy_url(url):
	"This is a hack that destroys query parameters"

	url = url.partition('#')[0] # Question marks aren't disallowed in the fragment identifier (I seem to recall)
	return url.partition('?')[0]

def blobify(url):
	MAPWIKI_USER = os.environ.get('MAPWIKI_USER', '')
	MAPWIKI_PASS = os.environ.get('MAPWIKI_PASS', '')

	url = tidy_url(url)

	print "Going to get URL: {0}".format(url)
	response = requests.get(url, auth=(MAPWIKI_USER, MAPWIKI_PASS), params={'action':'raw'}, verify='AnchorCA.pem')

	document = {}
	document['url']  = url
	document['blob'] = response.content

	# title
	# excerpt
	# last_updated
	# local_id = URL with the stem stripped off
	# title

	yield document

