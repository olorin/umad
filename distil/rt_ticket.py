import sys
import os
import re
from urllib import urlencode
from operator import itemgetter
from itertools import chain
import json
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
			'created',
			'private',
			)
	clean_msg = dict([ (k,v) for (k,v) in msg.iteritems() if k in fields_we_care_about ])

	# When we reply on a ticket, we get the ticket-wide subject if we don't specify a different Subject
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
	# This may be None if there's no Related Customer set
	customer_url       = ticket['customer_url']
	customer_visible   = True if not ticket['private'] else False

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

	# We see git@bitts rollin', we hatin'
	messages = [ m for m in messages if not m['from_email'].startswith('git@bitts') ]

	# Pull out the first post, we'll use it for the excerpt
	# XXX: Blindly assumes the first post has the lowest numerical ID, check with dev team whether this is correct
	messages.sort(key=itemgetter('_id'))
	# Some messages are empty or otherwise useless, so ignore them
	messages = [ m for m in messages if m['subject'] or m['content'] or m['from_email'] ]

	# XXX: Incurs an explosion if we get a ticket with no messages lol
	first_post = messages[0]
	# For some reason, the subject line sometimes appears to be empty. Not
	# sure if this is a problem with the ticket API.
	if not first_post['subject']:
		first_post['subject'] = ticket_subject
	first_post['content'] = '\n'.join( first_post['content'].split('\n')[:4] )
	ticket_excerpt = u"""{from_realname} <{from_email}> sent a mail with subject "{subject}", saying:\n{content} """.format(**first_post).encode('utf8')

	# Don't index deleted tickets
	if ticket_status == 'deleted':
		return

	# This is an empty list if the ticket has seen no actual communication (eg. internal-only tickets)
	contact_timestamps = [ parse(m['created']) for m in messages if not m['private'] ]


	# Put together our response. We have:
	# - ticket_url (string)
	# - ticket_subject (string)
	# - ticket_status (string)
	# - messages (iterable of dicts)

	# This is like running `sort | uniq` over all the message bodies
	all_message_lines = list(set(chain(*[ message['content'].split('\n') for message in messages ])))
	realnames         = list(set( [ x['from_realname'] for x in messages if x['from_realname'] != '' ] ))
	emails            = list(set( [ x['from_email']    for x in messages if x['from_email']    != '' ] ))

	blob = " ".join([
			ticket_number.encode('utf8'),
			ticket_subject.encode('utf8'),
			' '.join(realnames).encode('utf8'),
			' '.join(emails).encode('utf8'),
			' '.join(all_message_lines).encode('utf8'),
			])

	ticketblob = {
		'url':              ticket_url,
		'blob':             blob,
		'local_id':         ticket_number,
		'title':            ticket_subject, # printable as a document title
		'excerpt':          ticket_excerpt,
		'subject':          ticket_subject,
		'status':           ticket_status,
		'realname':         realnames,
		'email':            emails,
		'last_updated':     ticket_lastupdated,
		'customer_visible': customer_visible,
		}

	# Only set last_contact if it has meaning
	if contact_timestamps:
		ticketblob['last_contact'] = max(contact_timestamps).astimezone(tzutc())

	# Only set customer_url if the ticket has that metadata
	if customer_url:
		ticketblob['customer_url'] = customer_url

	yield ticketblob

