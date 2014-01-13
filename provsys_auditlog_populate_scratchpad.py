# XXX: should rewrite this as a generic util script, to populate the scratchpad
# and also to use for monitoring once backend features are available in provsys
# to allow search-by-ID

import sys
import re
import redis

class InvalidAuditlogPosition(Exception): pass

class HumanIsDeadMismatch(Exception): pass

def debug(msg):
	pass # Comment out the next line to suppress debug output
	#print msg


def main(argv=None):
	if argv is None:
		argv = sys.argv

	# Get input
	try:
		position = argv[1]
	except IndexError as e:
		raise InvalidAuditlogPosition("You didn't supply an auditlog position")

	if not re.match(r'^[1-9][0-9]*$', position):
		raise InvalidAuditlogPosition("Audit log position must be only digits")

	position = int(position)
	debug("Specified position is {0}".format(position))


	# Insert it
	auditlog_scratchpad = redis.StrictRedis(host='localhost', port=6379, db=0)
	auditlog_scratchpad.set('auditlog_position', position)


	# Fetch again as a sanity check, and return
	reread_position = auditlog_scratchpad.get('auditlog_position')
	reread_position = int(reread_position)
	debug("Recorded auditlog position is {0}".format(reread_position))

	if position != reread_position:
		raise HumanIsDeadMismatch("Mismatch between given position and value re-read from scratchpad, something bad and unexpected happened :( ")
	else:
		print "All done, position has been recorded as {0}".format(reread_position)

	return 0


if __name__ == "__main__":
	sys.exit(main())

