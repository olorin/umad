import moin_map
import gollum_docs
import local_file
import http_generic
import rt_ticket
import rt_ticket_query
import provsysservers
import provsysvlans
import provsysresource
import provsys


class BadUrl(Exception): pass

class NoUrlHandler(Exception): pass

class Distiller(object):
	def __init__(self, url, indexer_url=None):
		self.url = url
		self.indexer_url = indexer_url
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

			# Dodgy hackery to patch up URLs that aren't in the format we expect
			elif url.startswith('https://rt.engineroom.anchor.net.au/'):
				self.fetcher = rt_ticket
			elif url.startswith('rt://'):
				self.url = url.replace('rt://', 'https://rt.engineroom.anchor.net.au/Ticket/Display.html?id=')
				self.fetcher = rt_ticket

			elif url.startswith('https://docs.anchor.net.au/'):
				self.fetcher = gollum_docs

			elif url.startswith('https://ticket.api.anchor.com.au/ticket?'):
				self.fetcher = rt_ticket_query
			elif url.startswith('provsysservers://'):
				self.fetcher = provsysservers
			elif url.startswith('provsysvlans://'):
				self.fetcher = provsysvlans
			elif url.startswith('https://resources.engineroom.anchor.net.au/resources/'):
				self.fetcher = provsysresource
			elif url.startswith('provsys://'):
				self.fetcher = provsys
			elif url.startswith( ('http://', 'https://') ):
				self.fetcher = http_generic
			elif url.startswith('file:///'):
				self.fetcher = local_file
			elif url.startswith('example://your.url.here/'):
				self.fetcher = None
		except:
			raise BadUrl("Your URL '%s' is no good, in some way" % url)

		if self.fetcher is None:
			raise NoUrlHandler("We don't have a module that can handle that URL: %s" % url)


	def blobify(self):
		# XXX: Pass self.indexer_url through to each blobify function.
		# XXX: Should probably be properly-OO and have each distiller subclass this basic distiller.
		self.docs = self.fetcher.blobify(self.url)
