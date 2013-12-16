import sys
import os

import redis

import distil
from elasticsearch_backend import *


# XXX: maybe these should be to stdout instead of stderr, I dunno
def debug(msg, force_debug=False):
	if DEBUG or force_debug:
		sys.stderr.write(PID_PREFIX + str(msg) + '\n')
		sys.stderr.flush()

def mention(msg):
	sys.stderr.write(PID_PREFIX + str(msg) + '\n')
	sys.stderr.flush()


DEBUG = os.environ.get('UMAD_INDEXING_WORKER_DEBUG')
DEBUG = True
PID_PREFIX = '[pid {0}] '.format(os.getpid())
debug("Debug logging is enabled")



def index(url):
	debug("-" * len("URL: %s" % url))
	debug("URL: %s" % url)
	debug("-" * len("URL: %s" % url))

	d = distil.Distiller(url)

	for doc in d.docs:
		if doc is None:
			return
		debug("Adding to index: %(url)s" % doc)
		debug(doc['blob'][:400])
		add_to_index(doc['url'], doc)
		mention("Successfully added to index: %(url)s" % doc)
		debug("")




def main(argv=None):
	debug("Debug logging is enabled")

	teh_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

	while True:
		try:
			# Get URLs out of Redis. We're using this idiom to provide what is
			# effectively a "BSPOP" (blocking pop from a set), on a sorted set.
			# cf. Event Notification: http://redis.io/commands/blpop
			while True:
				pipeline = teh_redis.pipeline()
				pipeline.zrange('umad_indexing_queue', 0, 0)
				pipeline.zremrangebyrank('umad_indexing_queue', 0, 0)
				(urls, urlcount) = pipeline.execute() # Should return:  [ [maybe_single_url], {0|1} ]

				if not urls:
					break
				url = urls[0]

				index(url)

			debug("The barber is napping")
			teh_redis.brpop('barber')
			debug("------------------------")
			debug("The barber was woken up!")
		except Exception as e:
			debug("Something went boom: {0}".format(e))


	return 0


if __name__ == "__main__":
	sys.exit(main())
