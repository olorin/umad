#!/usr/bin/env python

import sys
import argparse
import requests

parser = argparse.ArgumentParser(description="Read URLs from stdin or files, and enqueue them for indexing/deletion")
parser.add_argument('input', type=argparse.FileType('r'), default=[sys.stdin], nargs='*', metavar="filename", help="Input file/s, defaults to stdin (-)")
parser.add_argument('-d', '--delete', action="store_true", help="Enqueue URLs for deletion instead of re/indexing")
parser.add_argument('--listener', default='http://localhost:8081/', help="URL of the UMAD listener [default: %(default)s]")
args = parser.parse_args()

request_method = requests.delete if args.delete else requests.get

for fh in args.input:
	for URL in fh.readlines():
		URL = URL.strip()
		if URL:
			r = request_method(args.listener, params={'url':URL.strip()})
			print r.text
