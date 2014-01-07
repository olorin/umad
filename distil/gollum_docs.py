import os
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests
# lxml to parse the HTML and grab the title
from lxml import html

# Plaintext-ify all the junk we get
import html2text


# XXX: constants go here

class FailedToRetrievePage(Exception):
	def __init__(self, msg):
		self.msg = msg

def tidy_url(url):
	"XXX: what's this for?"

	return url

def blobify(url):
	MAPWIKI_USER = os.environ.get('MAPWIKI_USER', '')
	MAPWIKI_PASS = os.environ.get('MAPWIKI_PASS', '')

	url = tidy_url(url)

	response = requests.get(url, auth=(MAPWIKI_USER, MAPWIKI_PASS))
	try:
		response.raise_for_status()
	except:
		raise FailedToRetrievePage("Error getting page from map wiki, got HTTP response {0} with error: {1}".format(response.status_code, response.reason) )


	# An example URL:  https://docs.anchor.net.au/system/anchor-wikis/Namespaces
	#
	# url      = https://docs.anchor.net.au/system/anchor-wikis/Namespaces
	# local_id = system/anchor-wikis/Namespaces
	# docs     = system/anchor-wikis/Namespaces
	# title    = Fetch from   <!-- --- title: THIS IS THE TITLE -->

	doc_tree = html.fromstring(response.text)
	content = html2text.html2text(response.text)
	# We could probably do this with lxml and some XPath, but meh
	content = content.replace('\n\n  * Search\n\n  * Home\n  * All\n  * Files\n  * New\n  * Upload\n  * Rename\n  * Edit\n  * History', '')
	content = content.replace('\n\n  * Search\n\n  * Home\n  * All\n  * New\n  * Upload\n  * Rename\n  * Edit\n  * History', '') # why is Files not always there?

	# XXX: We're assuming here that all pages across all wikis are in a single index and namespace
	# XXX: What if the page is empty? Might break a whole bunch of assumptions below this point.

	# Get the page name 
	page_name = url.replace('https://docs.anchor.net.au/', '')

	# Get the content
	page_lines = [ line.strip() for line in content.split('\n') ]

	# Kill empty lines and clean out footer
	page_lines = [ line for line in page_lines if line ]
	if page_lines[-1] == 'Delete this Page': del(page_lines[-1])
	if page_lines[-1].startswith('Last edited by '): del(page_lines[-1])

	# Local identifier will be the URL path components
	local_id = ' '.join( page_name.split('/') )

	# Pull the title from the HTML
	title_list = doc_tree.xpath('//title/text()')
	if title_list:
		title = title_list[0]
		# If we have a real document title, roll it into the local_id for searchability goodness
		local_id += " " + ' '.join(title.split())
	else:
		title = local_id


	# If we get this title, it means that the page doesn't exist, it was probably deleted.
	# XXX: Just bail out for now, but the correct action is to probably nuke the index entry.
	if title == 'Create a new page':
		return

	# The homepage of each repo is called Home, let's have something slightly more useful
	if title == 'Home':
		title = local_id

	# Content is now considered tidy
	blob = '\n'.join(page_lines)



	# Try and find an exciting excerpt, this is complete and utter guesswork
	indices_of_header_lines = [ i for i,x in enumerate(page_lines) if x.startswith('#') ]

	if len(indices_of_header_lines) >= 2:
		start,end = indices_of_header_lines[0:2]
	elif len(indices_of_header_lines) == 1:
		start = indices_of_header_lines[0]
		end   = start + 5 # magic number
	else:
		start,end = 0,-1

	excerpt = '\n'.join(page_lines[start+1:end]) # fencepost, not interested in the header line
	excerpt = excerpt[:500] # Not too much, guards against pathologically weird articles in particular


	# Good to go now
	document = {}
	document['url']  = url
	document['blob'] = blob
	document['local_id'] = local_id
	document['title']    = title
	document['excerpt']  = excerpt

	for key in document:
		print u"{0}\n\t{1}\n".format(key, document[key][:400])


	yield document

