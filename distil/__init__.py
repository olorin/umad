import moin_map
import local_file
import http_generic
import rt_ticket
import rt_ticket_query
import provsys


class BadUrl(Exception):
	def __init__(self, msg):
		self.msg = msg

class NoUrlHandler(Exception):
	def __init__(self, msg):
		self.msg = msg

class Distiller(object):
	def __init__(self, url):
		self.url = url
		self.fetcher = None
		self.docs = [] # Each element looks like:  { 'url':"foo", 'blob':"bar" }

		# Tidy the URL here if needed
		self.init_fetcher()
		self.blobify()


	def init_fetcher(self):
		'''Find a module with fetch and blobify capabilities that's suitable for the URL provided'''
		url = self.url

		try:
			#print "Testing for fetcher with url: %s (type is %s)" % (url, type(url))
			if url.startswith('https://map.engineroom.anchor.net.au/'):
				self.fetcher = moin_map
			elif url.startswith('https://rt.engineroom.anchor.net.au/'):
				self.fetcher = rt_ticket
			elif url.startswith('https://ticket.api.anchor.com.au/ticket?'):
				self.fetcher = rt_ticket_query
			elif url.startswith( ('http://', 'https://') ):
				self.fetcher = http_generic
			elif url.startswith('provsys://'):
				self.fetcher = provsys
			elif url.startswith('file:///'):
				self.fetcher = local_file
			elif url.startswith('example://your.url.here/'):
				self.fetcher = None
		except:
			raise BadUrl("Your URL '%s' is no good, in some way" % url)

		if self.fetcher is None:
			raise NoUrlHandler("We don't have a module that can handle that URL: %s" % url)


	def blobify(self):
		self.docs = self.fetcher.blobify(self.url)
