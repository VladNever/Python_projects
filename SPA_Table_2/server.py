from http.server import HTTPServer, CGIHTTPRequestHandler

server_address = ("127.0.0.1", 8000)
httpd = HTTPServer(server_address, CGIHTTPRequestHandler)
httpd.serve_forever()
