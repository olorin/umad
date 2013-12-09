import sys
import os

from bottle import route, request, default_app, abort


# Run with something like:
# gunicorn -- workers 4 --bind 127.0.0.1:9090 indexing_listener:application


def debug(msg, force_debug=False):
	if DEBUG or force_debug:
		sys.stderr.write(PID_PREFIX + str(msg) + '\n')
		sys.stderr.flush()


DEBUG = os.environ.get('UMAD_INDEXER_DEBUG')
PID_PREFIX = '[pid {0}] '.format(os.getpid())
debug("Debug logging is enabled")



@route('/')
def index():
	url = request.query.url or ''
	debug("URL to index: %s" % url)


	try:
		# XXX: Hey, hey, do that Redis thing!
		pass
	except Exception as e:
		abort(500, "Something went boom: {0}".format(e))


	return "Success, enqueued URL for indexing: {0}".format(url)



# For encapsulating in a WSGI container
application = default_app()

