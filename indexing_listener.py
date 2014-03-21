import sys
import os
import time

import redis

from bottle import route, request, default_app, abort


teh_redis = redis.StrictRedis(host='localhost', port=6379, db=0)


# XXX: maybe these should be to stdout instead of stderr, I dunno
def debug(msg, force_debug=False):
	if DEBUG or force_debug:
		msg_output = u"{0}{1}\n".format(PID_PREFIX, msg)
		sys.stderr.write(msg_output.encode('utf8'))
		sys.stderr.flush()


DEBUG = os.environ.get('UMAD_INDEXING_LISTENER_DEBUG')
PID_PREFIX = '[pid {0}] '.format(os.getpid())
debug("Debug logging is enabled")



@route('/', method=['GET','DELETE'])
def index():
	url = request.query.url or ''
	debug(u"URL to index: %s" % url)

	if not url:
		human_method = { 'GET':"index", 'DELETE':"delete" }.get(request.method, 'something-something-action')
		abort(400, "Y U DO DIS? I can't {0} something unless you give me 'url' as a query parameter".format(human_method))

	human_action = { 'GET':"indexing", 'DELETE':"deletion" }.get(request.method, 'something-something-action')

	try:
		if request.method == 'DELETE':
			queue_name  = 'umad_deletion_queue'
			barber_name = 'barber_deletion' # Not sure if we need a separate signalling channel, but it shouldn't hurt
		else:
			queue_name  = 'umad_indexing_queue'
			barber_name = 'barber'

		# Throw URLs into Redis. We're using this idiom to provide what is
		# effectively a "BSPOP" (blocking pop from a set), on a sorted set.
		# cf. Event Notification: http://redis.io/commands/blpop
		# I-It's not like I wanted the set to be sorted or anything! I'm
		# keeping input timestamps, just so you know.
		pipeline = teh_redis.pipeline()
		pipeline.zadd(queue_name, time.time(), url)
		pipeline.lpush(barber_name, 'dummy_value')
		pipeline.execute() # will return something like:   [ {0|1}, num_dummies ]
		debug(u"Successful insertion of {0} for {1}".format(url, human_action))
	except Exception as e:
		abort(500, "Something went boom: {0}".format(e))


	return u"Success, enqueued URL for {0}: '{1}'".format(human_action, url)



# For encapsulating in a WSGI container
application = default_app()
