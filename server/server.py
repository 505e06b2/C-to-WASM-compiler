from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import urllib

PORT_NUMBER = 8080

class myHandler(BaseHTTPRequestHandler):

    extensions = {"wasm": "application/wasm"}
    
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html") as f:
                self.wfile.write(f.read())
        else:
            path = urllib.unquote(self.path[1:])
            try:
                with open(path) as f:
                    ext = self.path.split('.')[-1]
                    self.send_response(200)
                    self.send_header("Content-type", self.extensions[ext])
                    self.end_headers()
                    self.wfile.write(f.read())
            except IOError:
                self.send_response(404)
                self.end_headers()
        return

try:
    server = HTTPServer(("", PORT_NUMBER), myHandler)
    print("Started httpserver on port:" , PORT_NUMBER)
    server.serve_forever()

except KeyboardInterrupt:
    print("^C received, shutting down the web server")
    server.socket.close()
