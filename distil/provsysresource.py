import sys
import os
import re
from urllib import urlencode
import json

from provisioningclient import *

def debug(msg=''):
	pass # uncomment the following line to enable debug output
	print msg


def os_to_document(os_resource):
	"Take an OS provsys resource, return a document to give to UMAD"

	resource_id  = os_resource._id
	os_name      = os_resource.name
	supportlevel = os_resource.details['supportlevel']
	version      = os_resource.details['version']
	release      = os_resource.details['release']
	distro       = os_resource.details['distro']
	collection   = os_resource.collection

	# Determine chassis and location
	chassis = os_resource.container
	chassistype = 'NOT_A_CHASSIS'
	locationtype = 'NOT_A_LOCATION'
	containedin = 'NOT_AN_OS_CONTAINER'

	if chassis is not None:
		# Some resources aren't "sane", we can't rely on them being in
		# a meaningful chassis and location.
		chassis.load(with_fields=['name', 'type','container']) # override lazy loading
		# "Virtual Machine" or "Rackmount Chassis"
		chassistype = chassis.type.name

		location = chassis.container
		if location is not None:
			location.load(with_fields=['name','type','container']) # override lazy loading
			# XXX: "something hypervisor something" or "Y" or "Z"
			locationtype = location.type.name

	# Get the type of container, either gets "Virtual Machine" or "Rackmount Chassis" I think
	if 'hypervisor' in locationtype.lower():
		hypervisor_os = location.container
		hypervisor_os.load(with_fields='name') # override lazy loading
		containedin = hypervisor_os.name
	else:
		# Probably a physical machine
		if location is not None:
			containedin = location.name
		if chassis is not None:
			if chassistype == "Rackmount Chassis" and chassis.name != os_name:
				chassistype = "Rackmount Chassis (%s)" % chassis.name

	# Debian is special
	if distro == 'Debian':
		pretty_name = release
	else:
		pretty_name = version

	# The uri seems to have auth credentials in it, which we want to strip
	uri = re.sub(r'(https?://)([^@]+@)?(.*)', r'\1\3', os_resource._uri)

	# Put it all together
	server_yieldable = {}
	digest = ''

	server_yieldable['url']      = uri
	server_yieldable['local_id'] = resource_id

	server_yieldable['name']  = os_name
	server_yieldable['title'] = os_name
	digest += ' '+os_name

	if collection:
		server_yieldable['customer'] = collection.name
		server_yieldable['taskid']   = collection.ourclientref
		digest += ' {0} {1}'.format(collection.name, collection.ourclientref)

	server_yieldable['distro'] = distro
	digest += ' '+distro

	server_yieldable['version'] = pretty_name
	digest += ' '+pretty_name

	server_yieldable['container'] = containedin
	digest += ' '+containedin

	server_yieldable['machinetype'] = chassistype
	digest += ' '+chassistype

	server_yieldable['support'] = supportlevel
	digest += ' '+supportlevel

	excerpt = "{name} is a {support} {machinetype} in {container}, running {distro} {version}. ".format(**server_yieldable)
	if collection:
		excerpt += "It belongs to {customer} (customer_id: {taskid}). ".format(**server_yieldable)

	server_yieldable['blob'] = digest.strip()
	server_yieldable['excerpt'] = excerpt.strip()

	return server_yieldable



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
	result = Resource.get(resource_id)
	try:
		result.load()
	except lib.provisioningobject.HTTPError as e:
		print "Resource {0} doesn't exist :(".format(resource_id)
		return

	resource = result
	oses_to_index = []

	# XXX: Performance! \o/
	#os_type_ids = [ x.id for x in Type.search(parent='Generic OS install') ]
	#   Linux&
	#   Windows&
	#   BSD&
	#   Other OS
	os_type_ids = [27, 28, 29, 36]

	# A bit more specialised, we're not using supertype='Generic Chassis'
	# because only certain chassis types are likely to be renamed.
	# 8/9/51 = Rackmount/Desktop/Colocated
	chassis_type_ids = [8, 9, 51]


	# Check if we're dealing with a chassis (a physical one that might be
	# renamed) and find all the OSes inside.
	if resource.type.id in chassis_type_ids:
		debug("Resource {0} is a chassis, will find OSes contained within".format(resource_id))
		this_chassis = resource
		child_oses = Resource.search(supertype="Generic OS install", container=this_chassis)
		for child_os in child_oses:
			debug("Enqueueing resource {0} for indexing".format(child_os.id))
			oses_to_index.append(child_os)

	# Or check if we've got an OS (supertype is "Generic OS install")
	elif resource.type.id in os_type_ids:
		debug("Resource {0} is an OS, will enqueue".format(resource_id))
		oses_to_index.append(resource)

	debug("Ready to index OSes")
	for os in oses_to_index:
		debug("Document'ing OS {0}".format(os.name))
		yield os_to_document(os)
