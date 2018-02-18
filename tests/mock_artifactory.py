#!/usr/bin/env python

import os
import SimpleHTTPServer
import SocketServer

port = 8080
response_path = os.path.join(os.path.abspath(__file__), 'response.json')


class LicenseHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(open(response_path).read())

SocketServer.TCPServer(("", port), LicenseHandler).serve_forever()
