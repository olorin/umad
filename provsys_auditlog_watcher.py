# Priming the scratchpad
# ======================

# Audit log entries have a unique monotonic increasing identifier. As such, we
# can follow the stream of auditlog events by fetching all entries newer than
# the last-seen, and logging our progress.

# The watcher needs to keep a position-marker of the newest (highest-numbered)
# seen-and-enqueued audit log entry. We use Redis for this scratchpad. As it is
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
import os
import re
import json
import requests
from urllib import urlencode
import time

from provsys_auditlog_lib import AuditlogScratchpad

class FailedToRetrieveAuditlogs(Exception): pass

class InvalidAuditlogEntryUrl(Exception): pass

def debug(msg=''):
	pass # uncomment the following line to enable debug output
	print msg


AUDITLOGS_URL = 'https://resources.engineroom.anchor.net.au/logs'
AUDITLOG_ENTRY_URL_RE = re.compile(r'^{0}/(\d+)$'.format(AUDITLOGS_URL))
UMAD_INDEXER_URL = 'https://umad-indexer.anchor.net.au/'

scratchpad = AuditlogScratchpad()
json_headers = {}
json_headers['Accept'] = 'application/json'
pres_key = "provsys_resource_id:{0}".format


def get_newer_than(last_known_good):
	response = requests.get(AUDITLOGS_URL, auth=('script','script'), verify='AnchorCA.pem', headers=json_headers, params={'id':'>{0}'.format(last_known_good), 'apikey':"UMAD provsys log watcher"})
	if response.status_code != 200:
		raise FailedToRetrieveAuditlogs("Didn't get a 200 Success while retrieving auditlog entries newer than {0}, something has exploded badly, bailing".format(last_known_good))

	auditlog_entries = json.loads(response.content)
	return auditlog_entries


def fetch_entry(resource_url):
	debug("Fetching auditlog entry: {0}".format(resource_url))
	response = requests.get(resource_url, auth=('script','script'), verify='AnchorCA.pem', headers=json_headers)
	if response.status_code != 200:
		raise FailedToRetrieveAuditlogs("Didn't get a 200 Success while retrieving auditlog entry {0}, something exploded, bailing".format(resource_url))

	auditlog_entry = json.loads(response.content)
	return auditlog_entry

def dump_entry(dikt):
	for key in dikt:
		if dikt[key]:
			print "\t{0}\n\t\t{1}".format(key, dikt[key])


def main(argv=None):
	if argv is None:
		argv = sys.argv

	# Find our feet
	auditlog_position = scratchpad()[0]
	debug("Last enqueued auditlog entry had ID {0}".format(auditlog_position))

	new_auditlog_entries = [ x.encode('utf8') for x in get_newer_than(auditlog_position) ]
	new_auditlog_entries.sort() # Super important! We must work in positive order otherwise we might miss entries

	last_successful_enqueued_url = None
	for url in new_auditlog_entries:
		new_auditlog_position = AUDITLOG_ENTRY_URL_RE.match(url)
		if not new_auditlog_position:
			raise InvalidAuditlogEntryUrl("How did we get this URL? It's not valid: {0}".format(url))
		new_auditlog_position = new_auditlog_position.group(1)

		entry = fetch_entry(url)
		last_updated_timestamp = entry['logDate']
		if entry['tablename'] == 'resource':
			# XXX: dump_entry( entry )
			# Now stash the 'logDate' in Redis and enqueue the 'record' (URL)
			resource_id  = entry['rowID']
			resource_url = entry['record']

			scratchpad.updated_resource(resource_id, last_updated_timestamp)


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
					debug("\tSuccess enqueueing {0}".format(resource_url))
				else:
					print "Didn't get a 200 Success while enqueueing resource URL {0}, HTTP status code {1}".format(resource_url, r.status_code)
			else:
				debug("\tJust enqueued that URL, skipping {0}".format(resource_url))


		else:
			debug("\tSkipping, don't care about a non-resource")

		# That was some good auditlog, have another helping.
		# Jump through some hoops to get a timezone-aware datetime and then render it accordingly.
		scratchpad(new_auditlog_position, last_updated_timestamp)
		debug("Saved new position {0} at time {1}".format(new_auditlog_position, last_updated_timestamp))


	# Bide our time until cron runs us again. Oh yes, we will have thee...
	return 0


if __name__ == "__main__":
	GHETTO_CRON_INTERVAL_SECONDS = os.environ.get('GHETTO_CRON_INTERVAL_SECONDS')
	if GHETTO_CRON_INTERVAL_SECONDS is not None:
		try:
			GHETTO_CRON_INTERVAL_SECONDS = int(GHETTO_CRON_INTERVAL_SECONDS)
		except ValueError as e:
			debug("Couldn't convert GHETTO_CRON_INTERVAL_SECONDS to an integer. Bailing.")
			sys.exit(2)
	rc = main()
	if GHETTO_CRON_INTERVAL_SECONDS:
		debug("Running in ghetto-cron mode, sleeping for {0} seconds before exiting...".format(GHETTO_CRON_INTERVAL_SECONDS))
		time.sleep(GHETTO_CRON_INTERVAL_SECONDS)
	sys.exit(rc)
