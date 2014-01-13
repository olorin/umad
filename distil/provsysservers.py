import re

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

	for result in results:
		supportlevel = result.details['supportlevel']
		version      = result.details['version']
		release      = result.details['release']
		distro       = result.details['distro']
		collection   = result.collection

		# Determine chassis here - with some special hacks for performance increases.
		machinechassis = result.container
		if not machinechassis: # should not get here if we're not looking at Deleted resources
			continue
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
		pretty_name = release if distro == 'Debian' else version

		# The uri seems to have auth credentials in it, which we want to strip
		uri = re.sub(r'(https?://)([^@]+@)?(.*)', r'\1\3', result._uri)


		# Put it all together
		server_yieldable = {}
		digest = ''

		server_yieldable['url']   = uri

		server_yieldable['name']  = result.name
		server_yieldable['title'] = result.name
		digest += ' '+result.name

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

		server_yieldable['machinetype'] = typeofmachine
		digest += ' '+typeofmachine

		server_yieldable['support'] = supportlevel
		digest += ' '+supportlevel


		excerpt = "{name} is a {support} {machinetype} in {container}, running {distro} {version}. ".format(**server_yieldable)
		if collection:
			excerpt += "It belongs to {customer} (customer_id: {taskid}). ".format(**server_yieldable)

		server_yieldable['blob'] = digest.strip()
		server_yieldable['excerpt'] = excerpt.strip()


		yield server_yieldable


