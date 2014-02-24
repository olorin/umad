'''Easy-peasy mass deletions from UMAD index, so long as you know the page's name.

Like so:
	python util_delete_map_page.py /file/full/of/URLs
'''

import fileinput
import elasticsearch_backend


for url in fileinput.input():
	url = url.strip()
	elasticsearch_backend.delete_from_index(url)
	print "Deleted %s" % url
