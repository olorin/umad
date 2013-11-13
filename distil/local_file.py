import sys




def blobify(filepath):
	if filepath.startswith('file:///'):
		filepath = filepath.replace('file://', '')
	# lol what is error checking?? And sanity in general, for lolhueg files...
	file_contents = open(filepath, 'rb').read()
	return [{ 'url':filepath, 'blob':file_contents }]

