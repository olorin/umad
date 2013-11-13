import sys
import os
import re
from urllib import urlencode
import json
# Fuck urllib2, that's effort. You may need to `pip install requests`.
# http://docs.python-requests.org/en/latest/index.html
import requests

from provisioningclient import *


class NoServerFound(Exception):
	def __init__(self, msg):
		self.msg = "Couldn't found a server with the name '%s'" % msg
class MultipleServersFound(Exception):
	def __init__(self, msg):
		self.msg = "Multiple servers found for '%s', can only handle a single result" % msg



def fetch(servername):
	server.requester    = 'umad_tma'
	server.uri          = 'https://resources.engineroom.anchor.net.au/'
	server.user         = "script"
	server.password     = "script"
	server.apikey       = "Sysadmin convenience script"
	server.ca_cert_file = None

	search_term = servername
	results = Resource.search(search_term, supertype="Generic OS install")
	if not results:
		results = Resource.search(search_term, supertype="Generic OS install", status="Any")

	# Sanity checking, we're really lame and can only handle exactly one result
	if not results:
		raise NoServerFound(search_term)
	if len(results) > 1:
		raise MultipleServersFound(search_term)
	result = results[0]

	supportlevel = result.details['supportlevel']
	version      = result.details['version']
	release      = result.details['release']
	distro       = result.details['distro']
	collection   = result.collection

	# Determine chassis here - with some special hacks for performance increases.
	machinechassis = result.container
	machinechassis.load(with_fields=['name', 'type','container']) # override lazy loading
	chassiscontainer = machinechassis.container
	chassiscontainer.load(with_fields=['name','type','container']) # override lazy loading
	typeofcontainer = chassiscontainer.type.name
	typeofmachine = machinechassis.type.name

	# Get the type of container, either gets "Virtual Machine" or "Rackmount Chassis" I think
	if re.search("hypervisor", typeofcontainer, flags=re.IGNORECASE):
		hypervisor_os = chassiscontainer.container
		hypervisor_os.load(with_fields='name') # override lazy loading
		containedin = hypervisor_os.name
	else:
		containedin = chassiscontainer.name
		if machinechassis.type.name == "Rackmount Chassis" and  machinechassis.name != result.name:
			typeofmachine = "Rackmount Chassis (%s)" % machinechassis.name

	# Debian is special
	if distro == 'Debian':
		pretty_name = release
	else:
		pretty_name = version

	# The uri seems to have auth credentials in it, which we want to strip
	uri = re.sub(r'(https?://)([^@]+@)?(.*)', r'\1\3', result._uri)
	print uri

	server_data = {}
	server_data['name'] = result.name
	server_data['distro'] = distro
	server_data['pretty_name'] = pretty_name
	server_data['customer_name'] = ''
	if collection:
		server_data['customer_name'] = "%s %s" % (collection.name, collection.ourclientref)
	server_data['container'] = "%s %s" % (typeofmachine, containedin)
	server_data['supportlevel'] = supportlevel

	return server_data



def blobify(servername):
	server_data = fetch(servername)
	return ' '.join( server_data.values() ).lower()

