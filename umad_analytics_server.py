#!/usr/bin/env python

from SimpleWebSocketServer.SimpleWebSocketServer import *
import json
import time

class SimpleMoo(WebSocket):
    def handleMessage(self):
        print self.data
    def handleConnected(self):
        print '{"event":"SERVER_clientConnect","timestamp":%.3f}' % time.time() 
    #def handleClose(self): print "I'm off a boat! (client disconnected)"

if __name__ == '__main__':
    SimpleSSLWebSocketServer('',9876, SimpleMoo,
            certfile="umad_crt",
            keyfile="umad_key").serveforever()
