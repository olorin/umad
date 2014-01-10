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
# Cache customer name lookups
import redis


class FailedToRetrieveTicket(Exception): pass

class MissingAuth(Exception): pass


#CUSTOMER_NAME_CACHE_TTL = 7 * 24 * 60 * 60 # 1 week, in seconds

AUDITLOG_ENTRY_URL_TEMPLATE = 'https://resources.engineroom.anchor.net.au/logs/{0}'.format


def main(argv=None):
	if argv is None:
		argv = sys.argv


	pass


	# Prime the scratchpad if needed
	auditlog_scratchpad = redis.StrictRedis(host='localhost', port=6379, db=0)
	auditlog_position = auditlog_scratchpad.get('auditlog_position')
	if not auditlog_position:
		auditlog_scratchpad.set('auditlog_position', 1)



	# Now fetch again
	auditlog_position = auditlog_scratchpad.get('auditlog_position')
	print auditlog_position

	# Keep fetching and incrementing until you get a 404


	auditlog_entry_url = AUDITLOG_ENTRY_URL_TEMPLATE(auditlog_position)
	headers = {}
	headers['Accept'] = 'application/json'

	auditlog_entry_response = requests.get(auditlog_entry_url, auth=('script','script'), verify='AnchorCA.pem', headers=headers)
	try:
		auditlog_entry_response.raise_for_status()
	except:
		raise FailedToRetrieveTicket("Couldn't get ticket from API, HTTP error %s, probably not allowed to view ticket" % auditlog_entry_response.status_code)

	auditlog_entry_json_blob = auditlog_entry_response.content # FIXME: add error-checking
	auditlog_entry = json.loads(auditlog_entry_json_blob)
	if 'code' in auditlog_entry: # we got a 404 or 403 or something, probably redundant after the raise_for_status check
		raise FailedToRetrieveTicket("Provsys hates us? %s" % str(auditlog_entry) )

	print auditlog_entry




	# Bail on the 404

	# We'll get run again by cron soon enough



#	parser = OptionParser()
#	parser.add_option("--verbose", "-v", dest="debug", action="store_true", default=False,       help="Log exactly what's happening")
#	parser.add_option("--bind", "-b",    dest="bind_host",                  default='localhost', help="Hostname/IP to listen on, [default: %default]")
#	parser.add_option("--port", "-p",    dest="bind_port", type="int",      default=8080,        help="Port number to listen on, [default: %default]")
#	(options, search_terms) = parser.parse_args(args=argv)



	return 0

if __name__ == "__main__":
	sys.exit(main())

