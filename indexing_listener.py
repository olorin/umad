import sys
import os
import time
from optparse import OptionParser

import redis

from bottle import route, request, run, default_app, abort


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
		else:
			queue_name  = 'umad_indexing_queue'

		# Throw URLs into Redis. We're using this idiom to provide what is
		# effectively a "BSPOP" (blocking pop from a set), on a sorted set.
		# cf. Event Notification: http://redis.io/commands/blpop
		# I-It's not like I wanted the set to be sorted or anything! I'm
		# keeping input timestamps, just so you know.
		pipeline = teh_redis.pipeline()
		pipeline.zadd(queue_name, time.time(), url)
		pipeline.lpush('barber', 'dummy_value')
		pipeline.execute() # will return something like:   [ {0|1}, num_dummies ]
		debug(u"Successful insertion of {0} for {1}".format(url, human_action))
	except Exception as e:
		abort(500, "Something went boom: {0}".format(e))


	return u"Success, enqueued URL for {0}: '{1}'".format(human_action, url)



# For encapsulating in a WSGI container
application = default_app()


def main(argv=None):
	if argv is None:
		argv = sys.argv

	parser = OptionParser()
	parser.add_option("--verbose", "-v", dest="debug", action="store_true", default=False,       help="Log exactly what's happening")
	parser.add_option("--bind", "-b",    dest="bind_host",                  default='localhost', help="Hostname/IP to listen on, [default: %default]")
	parser.add_option("--port", "-p",    dest="bind_port", type="int",      default=8081,        help="Port number to listen on, [default: %default]")
	(options, search_terms) = parser.parse_args(args=argv)

	global DEBUG
	DEBUG = options.debug

	run(host=options.bind_host, port=options.bind_port, debug=True)

	return 0

if __name__ == "__main__":
	sys.exit(main())
