# XXX: Could add features to also retrieve newer-than-X entries from the
# scratchpad, would be useful for monitoring perhaps.

import re
import redis

class InvalidAuditlogPosition(Exception): pass

class HumanIsDeadMismatch(Exception): pass

def debug(msg):
	pass # Comment out the next line to suppress debug output
	#print msg


class AuditlogScratchpad(object):
	def __init__(self, host='localhost', port=6379, db=0):
		self.conn = redis.StrictRedis(host=host, port=port, db=db, socket_timeout=1)
		self.conn.ping() # returns True or raises an exception

	def get(self):
		position = self.conn.get('auditlog_position')
		position = int(position)
		return position

	def set(self, new_position):
		new_position = str(new_position)
		if not re.match(r'^[1-9][0-9]*$', new_position):
			raise InvalidAuditlogPosition("Audit log position must be only digits")

		new_position = int(new_position)
		debug("Specified position is {0}".format(new_position))

		# Insert it
		self.conn.set('auditlog_position', new_position)

		# Fetch again as a sanity check, and return
		reread_position = self.get()
		debug("Recorded auditlog position is {0}".format(reread_position))

		if new_position != reread_position:
			raise HumanIsDeadMismatch("Mismatch between given position and value re-read from scratchpad, something bad and unexpected happened :( ")

		return reread_position
