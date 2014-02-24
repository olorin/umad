import sys
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests
# lxml to parse the HTML and grab the title
from lxml import html

# Plaintext-ify all the junk we get
import html2text


def tidy_url(url):
	"XXX: Not implemented yet"
	return url

def fetch(url):
	url = tidy_url(url)
	return requests.get(url, verify=True)

def blobify(url):
	response = fetch(url)

	content = html2text.html2text(response.text)
	doc_tree = html.fromstring(response.text)

	title_list = doc_tree.xpath('//title/text()')
	if title_list:
		title = title_list[0]
	else:
		title = url

	return [{ 'url':url, 'blob':content, 'title':title }]
