#!/usr/bin/env python

import SimpleHTTPServer
import SocketServer

PORT = 8080

class LicenseHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(open('licenses.json').read())

httpd = SocketServer.TCPServer(("", PORT), LicenseHandler)

print "serving at port", PORT
httpd.serve_forever()
