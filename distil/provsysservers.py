import re

from provsysresource import os_to_document
from provsysresource import debug

from provisioningclient import *


def blobify(UNUSED):
	server.requester    = 'umad_tma'
	server.uri          = 'https://resources.engineroom.anchor.net.au/'
	server.user         = "script"
	server.password     = "script"
	server.apikey       = "Sysadmin convenience script"
	server.ca_cert_file = None

	results = Resource.search(supertype="Generic OS install")
	if not results:
		return

	for os in results:
		debug("Document'ing OS {0}".format(os.name))
		yield os_to_document(os)
