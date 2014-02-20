#!/usr/bin/env python

from SimpleWebSocketServer.SimpleWebSocketServer import *
import json
import time
import sys
import os

# Force line buffering for running under daemontools
#
linebuffered_stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
def log(message):
	linebuffered_stdout.write(message)
	linebuffered_stdout.write("\n")
	linebuffered_stdout.flush()

class SimpleMoo(WebSocket):
	def handleMessage(self):
		log(self.data)
	def handleConnected(self):
		log('{"event":"SERVER_clientConnect","timestamp":%.3f}' % time.time() )

if __name__ == '__main__':
	SimpleSSLWebSocketServer('',9876, SimpleMoo,
		certfile="umad_crt",
		keyfile="umad_key").serveforever()
