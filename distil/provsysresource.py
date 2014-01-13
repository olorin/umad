import sys
import os
import re
from urllib import urlencode
import json

from provisioningclient import *

def blobify(url):
	'''Example URL: https://resources.engineroom.anchor.net.au/resources/10150 '''

	server.requester    = 'umad_tma'
	server.uri          = 'https://resources.engineroom.anchor.net.au/'
	server.user         = "script"
	server.password     = "script"
	server.apikey       = "Sysadmin convenience script"
	server.ca_cert_file = None

	# Get the resource
	resource_id = url.replace('https://resources.engineroom.anchor.net.au/resources/', '')
	resource = Resource.get(resource_id)
	try:
		resource.load()
	except lib.provisioningobject.HTTPError as e:
		print "Resource {0} doesn't exist :(".format(resource_id)
		return

	# Check that the supertype is "Generic OS install" or <something chassis>
	result = resource
	print result


	return

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

	server_data = {}
	server_data['name'] = result.name
	server_data['distro'] = distro
	server_data['pretty_name'] = pretty_name
	server_data['customer_name'] = ''
	if collection:
		server_data['customer_name'] = "%s %s" % (collection.name, collection.ourclientref)
	server_data['container'] = "%s %s" % (typeofmachine, containedin)
	server_data['supportlevel'] = supportlevel

	yield { 'url':uri, 'server_data':server_data }
