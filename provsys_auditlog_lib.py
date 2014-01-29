import re
import redis

class InvalidAuditlogPosition(Exception): pass

class HumanIsDeadMismatch(Exception): pass

class AuditlogPositionUnknown(Exception): pass

def debug(msg):
	pass # Comment out the next line to suppress debug output
	#print msg


RESOURCE_LASTUPDATED_CACHE_TTL = 7 * 24 * 60 * 60 # 1 week, in seconds
p_res_key = "provsys_resource_id:{0}".format


class AuditlogScratchpad(object):
	def __init__(self, host='localhost', port=6379, db=0):
		self.conn = redis.StrictRedis(host=host, port=port, db=db, socket_timeout=1)
		self.conn.ping() # returns True or raises an exception

	#yolo This is kind of abusive.
	def __call__(self, *args):
		if args:
			return self.set(*args)
		else:
			return self.get()

	def updated_resource(self, resource_id, last_updated_timestamp):
		self.conn.setex(p_res_key(resource_id), RESOURCE_LASTUPDATED_CACHE_TTL, last_updated_timestamp)

	def get(self):
		pipeline = self.conn.pipeline()
		pipeline.get('auditlog_position')
		pipeline.get('auditlog_position_timestamp')
		position, timestamp = pipeline.execute()

		if not position:
			raise AuditlogPositionUnknown("No record of current auditlog position, have you primed the scratchpad yet?")
		position = int(position)

		# XXX: ignore any timestamp problems right now

		return (position, timestamp)

	def set(self, new_position, position_timestamp):
		new_position = str(new_position)
		if not re.match(r'^[1-9][0-9]*$', new_position):
			raise InvalidAuditlogPosition("Audit log position must be only digits")

		new_position = int(new_position)
		debug("Specified position is {0}, timestamp is {1}".format(new_position, position_timestamp))

		# Insert it
		pipeline = self.conn.pipeline()
		pipeline.set('auditlog_position', new_position)
		pipeline.set('auditlog_position_timestamp', position_timestamp)
		pipeline.execute()

		# Fetch again as a sanity check, and return
		(reread_position, reread_timestamp) = self.get()
		debug("Recorded auditlog position is {0}, timestamp is {1}".format(reread_position, reread_timestamp))

		if new_position != reread_position:
			raise HumanIsDeadMismatch("Mismatch between given position and value re-read from scratchpad, something bad and unexpected happened :( ")
		if position_timestamp != reread_timestamp:
			raise HumanIsDeadMismatch("Mismatch between given timestamp and value re-read from scratchpad, something bad and unexpected happened :( ")

		return (reread_position, reread_timestamp)
