'''Easy-peasy mass deletions from UMAD index, so long as you know the page's name.

Like so:
	python util_delete_map_page.py /file/full/of/map/page/names
'''

import fileinput
import elasticsearch_backend


for url in fileinput.input():
	url = url.strip()
	elasticsearch_backend.delete_from_index(url)
	print "Deleted %s" % url

raise Exception("We're done now") # supah lazy

# This is just for Moin stuff
for page_name in fileinput.input():
	url = 'https://map.engineroom.anchor.net.au/{0}'.format(page_name.strip())
	print "%s" % url
	elasticsearch_backend.delete_from_index(url)

