import sys
import os
import re
from urllib import urlencode
import json

from provisioningclient import *

def debug(msg=''):
	pass # uncomment the following line to enable debug output
	print msg


def vlan_to_document(vlan_resource):
	"Take a VLAN resource, return a document to give to UMAD"

	resource_id      = vlan_resource.id
	collection       = vlan_resource.collection
	lifecycle_status = vlan_resource.status.name
	description      = vlan_resource.details['notes']
	vlan_shortname   = vlan_resource.name
	vlan_longname    = vlan_resource.details['vlan_longname']
	vlan_id          = vlan_resource.details['serialnum']

	location = vlan_resource.container
	location_name = location.name if location is not None else '' # I <3 ternary

	# The uri seems to have auth credentials in it, which we want to strip
	uri = re.sub(r'(https?://)([^@]+@)?(.*)', r'\1\3', vlan_resource._uri)

	# Put it all together
	vlan_yieldable = {}
	digest = ''

	vlan_yieldable['url']   = uri

	vlan_yieldable['name']           = "{0} {1}".format(vlan_id, vlan_shortname)
	vlan_yieldable['title']          = "VLAN {0} {1}".format(vlan_id, vlan_shortname)
	vlan_yieldable['vlan_shortname'] = vlan_shortname
	digest += ' '+vlan_yieldable['name']

	if collection:
		vlan_yieldable['customer_name'] = collection.name
		vlan_yieldable['customer_id']   = collection.ourclientref
		vlan_yieldable['customer']      = '{0} {1}'.format(collection.name, collection.ourclientref)
		digest += ' {0} {1}'.format(collection.name, collection.ourclientref)

	if location_name:
		vlan_yieldable['location'] = location_name
		digest += ' '+location_name

	vlan_yieldable['lifecycle_status'] = lifecycle_status

	if description:
		vlan_yieldable['description']      = description
	vlan_yieldable['vlan_id']          = vlan_id
	if vlan_longname:
		vlan_yieldable['vlan_longname'] = vlan_longname

	if lifecycle_status != 'Disposed':
		excerpt = "VLAN {vlan_id} ({vlan_shortname}) is a VLAN at {location}. ".format(**vlan_yieldable)
		if collection:
			excerpt += "It belongs to {customer_name} (customer_id: {customer_id}). ".format(**vlan_yieldable)
		if description:
			excerpt += "\nNotes: {description} ".format(**vlan_yieldable)
	else:
		excerpt = "VLAN {name} with ID {vlan_id} has been disposed. ".format(**vlan_yieldable)
		# Redo the digest, it's all bogus now
		digest = "{name}".format(**vlan_yieldable)

	vlan_yieldable['blob'] = digest.strip()
	vlan_yieldable['excerpt'] = excerpt.strip()

	return vlan_yieldable



def os_to_document(os_resource):
	"Take an OS provsys resource, return a document to give to UMAD"

	resource_id      = os_resource.id
	os_name          = os_resource.name
	supportlevel     = os_resource.details['supportlevel']
	version          = os_resource.details['version']
	release          = os_resource.details['release']
	distro           = os_resource.details['distro']
	os_wordsize      = os_resource.details['wordsize']
	support_notes    = os_resource.details['notes']
	# Not all OS types can be managed for maintenance
	maint_weekday    = os_resource.details.get('maint_weekday')
	maint_hour       = os_resource.details.get('maint_hour')
	maint_minute     = os_resource.details.get('maint_minute')
	maint_duration   = os_resource.details.get('maint_duration')
	collection       = os_resource.collection
	lifecycle_status = os_resource.status.name

	# Cleanup; some details are always defined but can be None if they're not set
	if not version: version = ''
	if not release: release = ''
	if not os_wordsize: os_wordsize = ''
	if os_wordsize: os_wordsize = "{0}-bit".format(os_wordsize)

	# Determine chassis and location
	chassis = os_resource.container
	chassistype = 'NOT_A_CHASSIS'
	locationtype = 'NOT_A_LOCATION'
	containedin = 'NOT_AN_OS_CONTAINER'

	location = None
	chassis_config_summary = None
	if chassis is not None:
		# Some resources aren't "sane", we can't rely on them being in
		# a meaningful chassis and location.
		chassis.load(with_fields=['name', 'type','container']) # override lazy loading
		# "Virtual Machine" or "Rackmount Chassis"
		chassistype = chassis.type.name
		# Get the hardware specs as well, if available
		chassis_config_summary = chassis.details.get('config_summary')

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
		server_yieldable['customer_name'] = collection.name
		server_yieldable['customer_id']   = collection.ourclientref
		server_yieldable['customer']      = '{0} {1}'.format(collection.name, collection.ourclientref)
		digest += ' {0} {1}'.format(collection.name, collection.ourclientref)

	server_yieldable['distro'] = distro
	digest += ' '+distro

	server_yieldable['version'] = pretty_name
	digest += ' '+pretty_name

	server_yieldable['os_wordsize'] = os_wordsize
	digest += ' '+os_wordsize

	server_yieldable['container'] = containedin
	digest += ' '+containedin

	server_yieldable['machinetype'] = chassistype
	digest += ' '+chassistype

	server_yieldable['support'] = supportlevel
	digest += ' '+supportlevel

	server_yieldable['lifecycle_status'] = lifecycle_status

	# These may be None or an empty string, depending on whether they've been set previously
	if all([ x not in (None, '', u'') for x in (maint_weekday, maint_hour, maint_minute, maint_duration) ]):
		server_yieldable['maint_weekday']  = maint_weekday
		server_yieldable['maint_hour']     = maint_hour
		server_yieldable['maint_minute']   = maint_minute
		server_yieldable['maint_duration'] = maint_duration
		server_yieldable['maint_time']     = "{maint_hour}:{maint_minute:02}".format(**server_yieldable)

	if support_notes:
		server_yieldable['support_notes'] = support_notes
		digest += ' '+support_notes

	if lifecycle_status != 'Disposed':
		excerpt = "{name} is a {support} {machinetype} in {container}, running {distro} {version} {os_wordsize}. ".format(**server_yieldable)
		if collection:
			excerpt += "It belongs to {customer_name} (customer_id: {customer_id}). ".format(**server_yieldable)
		if chassis_config_summary:
			excerpt += "It's got {0}. ".format(chassis_config_summary)
		if 'maint_time' in server_yieldable and 'maint_weekday' in server_yieldable:
			excerpt += "Maintenance occurs every {maint_weekday} at {maint_time}. ".format(**server_yieldable)
		if support_notes:
			excerpt += "\nNotes: {support_notes} ".format(**server_yieldable)
	else:
		if 'distro' in server_yieldable:  del server_yieldable['distro']
		if 'version' in server_yieldable: del server_yieldable['version']
		if 'support' in server_yieldable: del server_yieldable['support']

		excerpt = "{name} has been disposed. ".format(**server_yieldable)
		# Redo the digest, it's all bogus now
		digest = "{name}".format(**server_yieldable)

	server_yieldable['blob'] = digest.strip()
	server_yieldable['excerpt'] = excerpt.strip()

	return server_yieldable



def blobify(url):
	'''Example URL: https://resources.engineroom.anchor.net.au/resources/10150 '''

	server.requester    = 'umad_distiller'
	server.uri          = 'https://resources.engineroom.anchor.net.au/'
	server.user         = "script"
	server.password     = "script"
	server.apikey       = "umad_distiller"
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
	vlans_to_index = []


	# XXX: Performance! \o/
	# os_type_ids = [ x.id for x in Type.search(parent='Generic OS install') ]
	#   Linux&
	#   Windows&
	#   BSD&
	#   Other OS
	os_type_ids = [27, 28, 29, 36]

	# A bit more specialised, we're not using supertype='Generic Chassis'
	# because only certain chassis types are likely to be renamed.
	# 8/9/32/51 = Rackmount/Desktop/Virtual/Colocated
	chassis_type_ids = [8, 9, 32, 51]


	# Check if we're dealing with a chassis (a physical one that might be
	# renamed, or a virtual one that might be migrated) and find all the
	# OSes inside.
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

	# We now handle VLANs!
	# XXX: This is evil hardcoding
	elif resource.type.id == 65:
		debug("Resource {0} is a VLAN, will enqueue".format(resource_id))
		vlans_to_index.append(resource)

	debug("Ready to index OSes")
	for os in oses_to_index:
		debug("Document'ing OS {0}".format(os.name))
		yield os_to_document(os)

	debug("Ready to index VLANs")
	for vlan in vlans_to_index:
		debug("Document'ing VLAN {0}".format(vlan.name))
		yield vlan_to_document(vlan)
