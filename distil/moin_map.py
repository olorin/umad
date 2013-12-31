import os
import re
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests


TITLE_RE    = re.compile(r'<<Title(\((.*)\))?>>', re.I)
WIKIWORD_RE = re.compile(r'([a-z]+)([A-Z])')

class FailedToRetrievePage(Exception):
	def __init__(self, msg):
		self.msg = msg

def tidy_url(url):
	"This is a hack that destroys query parameters"

	url = url.partition('#')[0] # Question marks aren't disallowed in the fragment identifier (I seem to recall)
	return url.partition('?')[0]

def blobify(url):
	MAPWIKI_USER = os.environ.get('MAPWIKI_USER', '')
	MAPWIKI_PASS = os.environ.get('MAPWIKI_PASS', '')

	url = tidy_url(url)

	response = requests.get(url, auth=(MAPWIKI_USER, MAPWIKI_PASS), params={'action':'raw'}, verify='AnchorCA.pem')
	try:
		response.raise_for_status()
	except:
		raise FailedToRetrievePage("Error getting page from map wiki, got HTTP response %s" % response.status_code)

	# An example URL:  https://map.engineroom.anchor.net.au/PoP/SYD1/NetworkPorts
	#
	# url      = https://map.engineroom.anchor.net.au/PoP/SYD1/NetworkPorts
	# local_id = PoP/SYD1/NetworkPorts
	# map      = PoP/SYD1/NetworkPorts
	# title    = syd1 Network Port Allocations

	page_lines = [ line.strip() for line in response.content.split('\n') ]

	# Discard all lines beginning with one of: (keep line if all checks are not-hit)
	#  - Comment (#)
	#  - Macro (<<)
	#  - Table tags (||)
	page_lines = [ line for line in page_lines if  all( [ not line.startswith(x) for x in ['#', '||', '<<'] ] )  ]

	# Content is now considered tidy
	blob = '\n'.join(page_lines)

	# Get the page name as according to Moin
	page_name = url.replace('https://map.engineroom.anchor.net.au/', '')
	if page_name == '': # Special case for the home page
		page_name = 'ClueStick'


	# Try to find a suitable title
	lines_starting_with_title_macro = [ line for line in page_lines if line.startswith('<<Title') ]
	lines_starting_with_equals_sign = [ line for line in page_lines if line.startswith('=') ]

	title = None
	if lines_starting_with_title_macro:
		title_line = lines_starting_with_title_macro[0]
		title = TITLE_RE.sub(r'\2', title_line).strip('"\'')
	elif lines_starting_with_equals_sign:
		title_line = lines_starting_with_equals_sign[0]
		title = title_line.strip('= ')

	if not title: # Either got left with an empty string, or still None
		path_components = page_name.split('/')
		title = ' '.join([ WIKIWORD_RE.sub(r'\1 \2', x) for x in path_components ])

	# Try and find an exciting excerpt, this is complete and utter guesswork
	indices_of_lines_beginning_with_equals_sign = [ i for i,x in enumerate(page_lines) if x.startswith('=') ]

	if len(indices_of_lines_beginning_with_equals_sign) >= 2:
		start,end = indices_of_lines_beginning_with_equals_sign[0:2]
	elif len(indices_of_lines_beginning_with_equals_sign) == 1:
		start = indices_of_lines_beginning_with_equals_sign[0]
		end   = start + 5 # magic number
	else:
		start,end = 0,-1

	excerpt = '\n'.join(page_lines[start+1:end]) # fencepost, not interested in the header line

	# Allow for title keyword searching
	map_rough_title_chunks  = set(page_name.split('/'))
	map_rough_title_chunks |= set([ WIKIWORD_RE.sub(r'\1 \2', x) for x in map_rough_title_chunks ])
	print "XXX"
	print map_rough_title_chunks

	document = {}
	document['url']  = url
	document['blob'] = blob
	document['local_id'] = page_name
	#document['map']      = ' '.join(map_rough_title_chunks)
	document['title']    = title
	document['excerpt']  = excerpt

	yield document

