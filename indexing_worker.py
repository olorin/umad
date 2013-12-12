import sys
import os

import redis

DEBUG = os.environ.get('UMAD_INDEXING_WORKER_DEBUG')
DEBUG = True
PID_PREFIX = '[pid {0}] '.format(os.getpid())


def debug(msg, force_debug=False):
	if DEBUG or force_debug:
		sys.stderr.write(PID_PREFIX + str(msg) + '\n')
		sys.stderr.flush()



def main(argv=None):
	debug("Debug logging is enabled")

	teh_redis = redis.Redis(host='localhost', port=6379, db=0)


	while True:
		debug("About to loop")
		try:
			# Get URLs out of Redis. We're using this idiom to provide what is
			# effectively a "BSPOP" (blocking pop from a set).
			# cf. Event Notification: http://redis.io/commands/blpop
			while True:
				url = teh_redis.spop('umad_indexing_queue')
				if url is None:
					break
				debug("Processing url %s" % url)
				pass # do something here

			debug("about to barber")
			teh_redis.brpop('barber')
			debug("woke up")
		except Exception as e:
			debug("Something went boom: {0}".format(e))


	return 0


if __name__ == "__main__":
	sys.exit(main())
