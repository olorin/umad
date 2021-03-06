import sys
import os
import re
from urllib import urlencode
import json
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests


# XXX: This distiller is obsolete and should be removed, it's doesn't do all
# the nice things that the real RT distiller does, and isn't really needed now
# that we have proper indexing infrastructure.


class MissingAuthToken(Exception): pass


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


def blobify_messages(messages):
	return ' '.join([ "%(content)s %(subject)s %(from_realname)s %(from_email)s" % message for message in messages ])


def fetch(url):
	# Buckle up, kiddo
	auth_token = os.environ.get('API_AUTH_TOKEN')
	if not auth_token:
		raise MissingAuthToken("We need your Anchor API auth token in the environment somewhere, 'API_AUTH_TOKEN'")

	headers = {}
	headers['Authorization'] = 'AA-Token %s' % auth_token
	headers['Accept'] = 'application/json'

	# Get ALL the tickets! \o/
	r = requests.get(url, verify=True, headers=headers)
	try:
		r.raise_for_status()
	except:
		print >>sys.stderr, "There was an error, got HTTP response %s" % r.status_code
		return

	tickets = json.loads(r.content) # XXX: add error-checking

	# Index 'em
	for ticket in tickets:
		if 'code' in ticket: # we got a 404 or 403 or something
			continue

		ticket_url     = WEB_TICKET_URL_TEMPLATE % ticket
		ticket_subject = ticket['subject']
		ticket_status  = ticket['status']

		messages_response  = requests.get(ticket['ticket_messages_url'], verify=True, headers=headers)
		messages = json.loads(messages_response.content) # XXX: add error-checking
		messages = [ clean_message(x) for x in messages ]

		yield { 'url':ticket_url, 'subject':ticket_subject, 'status':ticket_status, 'messages':messages }



def blobify(url):
	ticketblobs = [ {
		'url':       ticket['url'],
		'blob':      "%s %s" % ( ticket['subject'], blobify_messages(ticket['messages']) ),
		'name':      ticket['subject'], # printable as a document title
		'subject':   ticket['subject'],
		'status':    ticket['status'],
		'realnames': list(set( [ x['from_realname'] for x in ticket['messages'] if x['from_realname'] != '' ] )),
		'emails':    list(set( [ x['from_email'] for x in ticket['messages'] if x['from_email'] != '' ] )),
		} for ticket in fetch(url) ]

	return ticketblobs

