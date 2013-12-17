import sys
import os
import re
from urllib import urlencode
from operator import itemgetter
from itertools import chain
import json
import datetime
# dateutil is a useful helper library, you may need to install the
# `python-dateutil` package especially
from dateutil.parser import *
from dateutil.tz import *
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests


class FailedToRetrieveTicket(Exception):
	def __init__(self, msg):
		self.msg = msg

class BadRtUrl(Exception):
	def __init__(self, msg):
		self.msg = msg

class MissingAuth(Exception):
	def __init__(self, msg):
		self.msg = msg


TICKET_URL_TEMPLATE = 'https://ticket.api.anchor.com.au/ticket/%s'
TICKET_MESSAGE_URL_TEMPLATE = 'https://ticket.api.anchor.com.au/ticket_message?%s'
WEB_TICKET_URL_TEMPLATE = 'https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=%(_id)s'

TICKET_UNSTALL_RE = re.compile(r'The ticket \d+ has not received a reply from the requestor for.*Get on the phone with the client right now', re.I)


def clean_message(msg):
	fields_we_care_about = (
			'_id',
			'from_email',
			'from_realname',
			'content',
			'subject',
			)
	clean_msg = dict([ (k,v) for (k,v) in msg.iteritems() if k in fields_we_care_about ])

	# I dunno why we sometimes get this
	if clean_msg['subject'] == 'No Subject':
		clean_msg['subject'] = ''

	# Message body cleanup, attempt to nuke junk
	body_lines = clean_msg['content'].split('\n')
	body_lines = [ line.strip() for line in body_lines ]                     # Remove leading and trailing whitespace for later compaction
	body_lines = [ line for line in body_lines if not line.startswith('>') ] # Quoted lines
	body_lines = [ line for line in body_lines if not line == '' ]           # Empty lines
	if 'Regards,' in body_lines:                                             # Kill trailing platitudes
		body_lines = body_lines[:body_lines.index('Regards,')]
	if '--' in body_lines:                                                   # Kill signatures
		body_lines = body_lines[:body_lines.index('--')]

	# And put it all back together again
	clean_msg['content'] = '\n'.join(body_lines)

	# Sloppiness in the ticket API?
	if clean_msg['from_email'] is None:
		clean_msg['from_email'] = ''

	# Sloppiness in the ticket API?
	if clean_msg['from_realname'] is None:
		clean_msg['from_realname'] = ''

	# Kill quotemarks around names
	clean_msg['from_realname'] = clean_msg['from_realname'].strip("'\"")

	# Don't index the automated comment that gets added when a ticket unstalls itself
	if TICKET_UNSTALL_RE.search(clean_msg['content']):
		clean_msg['content'] = ''

	return clean_msg


# Expect an URL of form:
# https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=152
def tidy_url(url):
	"Turn the RT URL into an API URL"
	rt_url_match = re.match(r'https://rt\.engineroom\.anchor\.net\.au/Ticket/\w+\.html\?id=(\d+)', url)
	if rt_url_match is None:
		raise BadRtUrl("This URL doesn't match our idea of an RT URL: %s" % url)
	ticket_number = rt_url_match.group(1)

	ticket_url = TICKET_URL_TEMPLATE % ticket_number
	ticket_messages_url = TICKET_MESSAGE_URL_TEMPLATE % urlencode({'ticket_url': ticket_url})

	return (ticket_url, ticket_messages_url)


def blobify(url):
	# Note to self: yield'ing is cool. Either yield, return None, or raise
	# an exception. The latter is some other poor schmuck's problem.

	# Prepare auth
	auth_user = os.environ.get('API_AUTH_USER')
	auth_pass = os.environ.get('API_AUTH_PASS')
	if not auth_user or not auth_pass:
		raise MissingAuth("You must provide Anchor API credentials, please set API_AUTH_USER and API_AUTH_PASS")

	# Prep URL and headers for requests
	ticket_url, messages_url = tidy_url(url)
	headers = {}
	headers['Accept'] = 'application/json'

	# Get ticket from API
	ticket_response = requests.get(ticket_url, auth=(auth_user,auth_pass), verify=True, headers=headers)
	try:
		ticket_response.raise_for_status()
	except:
		raise FailedToRetrieveTicket("Error getting Ticket from API, got HTTP response %s" % ticket_response.status_code)

	# Mangle ticket until no good
	ticket_json_blob = ticket_response.content # FIXME: add error-checking
	ticket = json.loads(ticket_json_blob)
	if 'code' in ticket: # we got a 404 or 403 or something, probably redundant after the raise_for_status check
		raise FailedToRetrieveTicket("Ticket API hates us? %s" % str(ticket) )

	ticket_url         = WEB_TICKET_URL_TEMPLATE % ticket # Canonicalise the ticket URL, as merged tickets could have been accessed by multiple URLs
	ticket_number      = "{_id}".format(**ticket)
	ticket_subject     = ticket['subject']
	ticket_status      = ticket['status']
	ticket_lastupdated = ticket['lastupdated']

	# Get a real datetime object, let ElasticSearch figure out the rest
	ticket_lastupdated = parse(ticket_lastupdated)
	ticket_lastupdated = ticket_lastupdated.astimezone(tzutc())

	# Get associated messages from API
	messages_response  = requests.get(messages_url, auth=(auth_user,auth_pass), verify=True, headers=headers)
	try:
		messages_response.raise_for_status()
	except:
		raise FailedToRetrieveTicket("Error getting Messages from API, got HTTP response %s" % messages_response.status_code)

	# Mangle messages until no good
	messages_json_blob = messages_response.content # FIXME: add error-checking
	messages = json.loads(messages_json_blob)
	messages = [ clean_message(x) for x in messages ]

	# Pull out the first post, we'll use it for the excerpt
	# XXX: Blindly assumes the first post has the lowest numerical ID, check with dev team whether this is correct
	messages.sort(key=itemgetter('_id'))
	# XXX: Incurs an explosion if we get a ticket with no messages lol
	first_post = messages[0]
	first_post['content'] = '\n'.join( first_post['content'].split('\n')[:4] )
	ticket_excerpt = """{from_realname} <{from_email}> sent a mail with subject "{subject}", saying:\n{content} """.format(**first_post)

	# Don't index deleted tickets
	if ticket_status == 'deleted':
		return


	# Put together our response. We have:
	# - ticket_url (string)
	# - ticket_subject (string)
	# - ticket_status (string)
	# - messages (iterable of dicts)

	# This is like running `sort | uniq` over all the messages
	all_message_lines = list(set(chain(*[ message['content'].split('\n') for message in messages ])))

	# XXX: continue work here, use all_message_lines for the content body instead
	# XXX: also trim the excerpt to a sane size, not all of the first message
	message_texts = '\n\t'.join([ "%(content)s %(subject)s %(from_realname)s %(from_email)s" % message for message in messages ])
	blob = '%s %s' % (ticket['subject'], message_texts)
	ticketblob = {
		'url':          ticket_url,
		'blob':         blob,
		'local_id':     ticket_number,
		'title':        ticket_subject, # printable as a document title
		'excerpt':      ticket_excerpt,
		'subject':      ticket_subject,
		'status':       ticket_status,
		'realname':     ', '.join(  list(set( [ x['from_realname'] for x in messages if x['from_realname'] != '' ] ))  ),
		'email':        ', '.join(  list(set( [ x['from_email']    for x in messages if x['from_email']    != '' ] ))  ),
		'last_updated': ticket_lastupdated,
		'last_indexed': datetime.datetime.now(tzutc()),
		}

	yield ticketblob

