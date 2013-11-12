import sys
import os
import json
import requests
from optparse import OptionParser
from colorama import init as init_colorama
from termcolor import colored

import distil
from anchor_riak_connectivity import *

class MissingAuthToken(Exception):
	def __init__(self, msg):
		self.msg = msg


DEBUG = False
def debug(msg):
	if DEBUG:
		sys.stderr.write(str(msg) + '\n')
		sys.stderr.flush()

def debug_red(msg):
	debug(colored(msg, 'red'))
def debug_green(msg):
	debug(colored(msg, 'green'))


def clean_message(msg):
	clean_msg = dict([(k,msg[k]) for k in msg if k in ('from_email', 'from_realname', 'content', 'subject') ])
	if clean_msg['subject'] == 'No Subject':
		clean_msg['subject'] = ''
	clean_msg['content'] = clean_msg['content'].replace('\n',' ')
	if clean_msg['from_email'] is None:
		clean_msg['from_email'] = ''
	if clean_msg['from_realname'] is None:
		clean_msg['from_realname'] = ''
	return clean_msg


def main(argv=None):
	init_colorama()
	global DEBUG

	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.set_defaults(action=None)
	parser.add_option("--verbose", "-v", dest="debug",     action="store_true", default=False,     help="Log exactly what's happening")
	(options, urls) = parser.parse_args(args=argv)

	DEBUG = options.debug

	url = urls[1]
	debug("Your query is: %s" % url)
	assert(url.startswith('https://ticket.api.anchor.com.au/ticket?'))


	# Buckle up, kiddo
	auth_token = os.environ.get('API_AUTH_TOKEN')
	if not auth_token:
		raise MissingAuthToken("We need your Anchor API auth token in the environment somewhere, 'API_AUTH_TOKEN'")

	headers = {}
	headers['Authorization'] = 'AA-Token %s' % auth_token
	headers['Accept'] = 'application/json'


	# Get ALL the tickets! \o/
	r = requests.get(url, verify=True, headers=headers)
	tickets = json.loads(r.content)
	debug_green("Found %s tickets" % len(tickets))


	# Index 'em
	for ticket in tickets:
		ticket_subject = ticket['subject']
		ticket_url     = ticket['_url']
		messages_url   = ticket['ticket_messages_url']

		messages_response  = requests.get(messages_url, verify=True, headers=headers)
		messages_json_blob = messages_response.content # FIXME: add error-checking
		messages = json.loads(messages_json_blob)
		messages = [ clean_message(x) for x in messages ]

		blob = "%s %s" % (ticket_subject, ' '.join([ "%(content)s %(subject)s %(from_realname)s %(from_email)s" % message for message in messages ]) )

		debug_red("-" * len("URL: %s" % ticket_url))
		debug_red("URL: %s" % ticket_url)
		debug_red("-" * len("URL: %s" % ticket_url))
		print blob
		print

		add_to_index(ticket_url, blob)
		debug_green("Added to index: %s" % ticket_url)


	return 0


if __name__ == "__main__":
	sys.exit(main())

