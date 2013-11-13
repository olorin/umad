import sys
import os
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests


def tidy_url(url):
	"This is an awful hack that might destroy query parameters"
	url = url.partition('#')[0]
	urlparts = url.partition('?')
	if urlparts[2]: # We have query terms
		return '&'.join([ urlparts[0]+'?action=raw', urlparts[2] ])
	else: # No query terms
		return urlparts[0]+'?action=raw'

def blobify(url):
	RAGEWIKI_USER = os.environ.get('RAGEWIKI_USER', '')
	RAGEWIKI_PASS = os.environ.get('RAGEWIKI_PASS', '')

	url = tidy_url(url)
	response = requests.get(url, auth=(RAGEWIKI_USER, RAGEWIKI_PASS), verify='AnchorCA.pem')

	return [{ 'url':url, 'blob':response.content }]

