import sys
import os
import re
from urllib import urlencode
import json
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

def clean_message(msg):
	"msg is a dictionary, we care about subject, from_email, from_realname, content"
	clean_msg = dict([(k,msg[k]) for k in msg if k in ('from_email', 'from_realname', 'content', 'subject') ])

	if clean_msg['subject'] == 'No Subject':
		clean_msg['subject'] = ''
	clean_msg['content'] = clean_msg['content'].replace('\n',' ')

	if clean_msg['from_email'] is None:
		clean_msg['from_email'] = ''
	if clean_msg['from_realname'] is None:
		clean_msg['from_realname'] = ''

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


def fetch(url):
	auth_user = os.environ.get('API_AUTH_USER')
	auth_pass = os.environ.get('API_AUTH_PASS')
	if not auth_user or not auth_pass:
		raise MissingAuth("You need to provide authentication credential for Anchor APIs, please set API_AUTH_USER and API_AUTH_PASS")

	headers = {}
	headers['Accept'] = 'application/json'

	ticket_url, messages_url = tidy_url(url)

	ticket_response = requests.get(ticket_url, auth=(auth_user,auth_pass), verify=True, headers=headers)
	try:
		ticket_response.raise_for_status()
	except:
		print >>sys.stderr, "There was an error, got HTTP response %s" % ticket_response.status_code
		return None

	ticket_json_blob = ticket_response.content # FIXME: add error-checking
	ticket = json.loads(ticket_json_blob)
	if 'code' in ticket: # we got a 404 or 403 or something, probably redundant after the raise_for_status check
		return None

	ticket_url = WEB_TICKET_URL_TEMPLATE % ticket # Canonicalise the ticket URL, as merged tickets could have been accessed by multiple URLs
	ticket_subject = ticket['subject']
	ticket_status = ticket['status']

	messages_response  = requests.get(messages_url, verify=True, headers=headers)
	messages_json_blob = messages_response.content # FIXME: add error-checking
	messages = json.loads(messages_json_blob)
	messages = [ clean_message(x) for x in messages ]

	return {'url':ticket_url, 'subject':ticket_subject, 'messages':messages, 'status':ticket_status}



def blobify(url):
	ticket = fetch(url)
	if ticket is None:
		return []

	message_texts = ' '.join([ "%(content)s %(subject)s %(from_realname)s %(from_email)s" % message for message in ticket['messages'] ])
	blob = '%s %s' % (ticket['subject'], message_texts)
	ticketblob = [ {
		'url':       ticket['url'],
		'blob':      blob,
		'name':      ticket['subject'], # printable as a document title
		'subject':   ticket['subject'],
		'status':    ticket['status'],
		'realnames': list(set( [ x['from_realname'] for x in ticket['messages'] if x['from_realname'] != '' ] )),
		'emails':    list(set( [ x['from_email'] for x in ticket['messages'] if x['from_email'] != '' ] )),
		} ]

	return ticketblob

