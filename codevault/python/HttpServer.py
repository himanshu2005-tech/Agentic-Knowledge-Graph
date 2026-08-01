# Auto-generated Code Vault for 'HttpServer' [Python]

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class HttpServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info(f"Received GET request for {self.path}")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello, World! This is a basic HTTP server implemented in Python.")

    def do_POST(self):
        logging.info(f"Received POST request for {self.path}")
        content_length = int(self.headers["Content-Length"])
        post_body = self.rfile.read(content_length)
        logging.info(f"POST request body: {post_body}")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"POST request received successfully.")

def run_http_server(server_class=HTTPServer, handler_class=HttpServerHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_http_server()
