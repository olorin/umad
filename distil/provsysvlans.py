import re

from provsysresource import vlan_to_document
from provsysresource import debug

from provisioningclient import *


def blobify(UNUSED):
	server.requester    = 'umad_tma'
	server.uri          = 'https://resources.engineroom.anchor.net.au/'
	server.user         = "script"
	server.password     = "script"
	server.apikey       = "Sysadmin convenience script"
	server.ca_cert_file = None

	results = Resource.search(supertype="VLAN Definition")
	if not results:
		return

	for vlan in results:
		debug("Document'ing VLAN {0}".format(vlan.name))
		yield vlan_to_document(vlan)
