# Priming the scratchpad
# ======================

# Audit log entries have a unique monotonic increasing identifier, and it is
# believed that the numberline is non-sparse except in very rare cases (which
# can be tested for). As such, we can follow all audit entries by incrementing
# our counter and attempting to fetch the corresponding audit log entry.

# The watcher needs to keep a position-marker of the oldest (lowest-numbered)
# not-yet-fetched audit log entry. We use Redis for this scratchpad. As it is
# currently too complex to initially-populate the scratchpad from this code, it
# is a one-time manual process.

# 1. Visit the audit log web interface:
#      https://resources.engineroom.anchor.net.au/logs

# 2. Pick any visible entry and refer to the Date column. Get the target URL of
# the link and note the audit log entry ID, the final path component. Eg. for
# audit entry #123456 the URL is:
#      https://resources.engineroom.anchor.net.au/logs/123456

# 3. Run the scratchpad populator script with the log entry ID that you picked:
#      python provsys_auditlog_populate_scratchpad.py 123456

# 4. The auditlog watcher is now ready to run.


import sys
import json
import requests
from urllib import urlencode
import redis

class FailedToRetrieveAuditlogEntry(Exception): pass

def debug(msg=''):
	pass # uncomment the following line to enable debug output
	#print msg


AUDITLOG_ENTRY_URL_TEMPLATE = 'https://resources.engineroom.anchor.net.au/logs/{0}'.format
RESOURCE_LASTUPDATED_CACHE_TTL = 7 * 24 * 60 * 60 # 1 week, in seconds
UMAD_INDEXER_URL = 'https://umad-indexer.anchor.net.au/'


def main(argv=None):
	if argv is None:
		argv = sys.argv

	json_headers = {}
	json_headers['Accept'] = 'application/json'
	pres_key = "provsys_resource_id:{0}".format
	last_successful_enqueued_url = None


	# Find our feet
	auditlog_scratchpad = redis.StrictRedis(host='localhost', port=6379, db=0)
	auditlog_position = auditlog_scratchpad.get('auditlog_position')
	debug("Will look for next auditlog entry with ID {0}".format(auditlog_position))

	# Keep fetching and incrementing until you get a 404
	while True:
		debug("Fetching auditlog entry with ID {0}".format(auditlog_position))
		auditlog_entry_url = AUDITLOG_ENTRY_URL_TEMPLATE(auditlog_position)

		auditlog_entry_response = requests.get(auditlog_entry_url, auth=('script','script'), verify='AnchorCA.pem', headers=json_headers)
		if auditlog_entry_response.status_code == 404:
			debug("Got a 404 Not Found for auditlog entry {0}, assume we've caught up with all auditlog events".format(auditlog_position))
			break
		if auditlog_entry_response.status_code != 200:
			print "Didn't get a 200 Success trying to retrieve auditlog entry {0}, something has exploded badly, bailing".format(auditlog_position)
			return 1

		auditlog_entry_json_blob = auditlog_entry_response.content # FIXME: add sanity checking
		auditlog_entry = json.loads(auditlog_entry_json_blob)

		# Only resources matter
		if auditlog_entry['tablename'] == 'resource':
			# Now stash the 'logDate' in Redis and enqueue the 'record' (URL)
			resource_id  = auditlog_entry['rowID']
			resource_url = auditlog_entry['record']
			last_updated_timestamp = auditlog_entry['logDate']

			auditlog_scratchpad.setex(pres_key(resource_id), RESOURCE_LASTUPDATED_CACHE_TTL, last_updated_timestamp)

			# Don't bother enqueueing again if we just did it. This
			# behaviour relies on the fact that this process is
			# rather short-lived, otherwise the same resource being
			# updated twice consecutively, but with a large gap
			# inbetween, would result in the second update being
			# ignored.
			if resource_url != last_successful_enqueued_url:
				r = requests.get(UMAD_INDEXER_URL, params={'url':resource_url}, verify='AnchorCA.pem')
				if r.status_code == 200:
					last_successful_enqueued_url = resource_url
					debug("Success enqueueing {0}".format(resource_url))
				else:
					print "Didn't get a 200 Success while enqueueing resource URL {0}, HTTP status code {1}".format(resource_url, r.status_code)
			else:
				debug("Just enqueued that URL, skipping {0}".format(resource_url))
		else:
			debug("Skipping, don't care about a non-resource")


		# That was some good auditlog, have another helping
		auditlog_position = auditlog_scratchpad.incr('auditlog_position')
		debug()


	# Bide our time until cron runs us again. Oh yes, we will have thee...
	return 0


if __name__ == "__main__":
	sys.exit(main())
