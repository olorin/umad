import sys
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests

def tidy_url(url):
	"XXX: Not implemented yet"
	return url

def fetch(url):
	url = tidy_url(url)
	return requests.get(url, verify=True)

def blobify(url):
	response = fetch(url)
	return [{ 'url':url, 'blob':response.content }]


