from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>RSS Summaries</title></head>", "utf-8"))
        self.wfile.write(bytes("<button type=\"button\">Scrape Articles</button>", "utf-8"))
        self.wfile.write(bytes("<button type=\"button\">Show Summaries</button>", "utf-8"))
        
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        #for i in categories:
        #   self write Category
        #   self write Body
        #   self write urls, titles
        self.wfile.write(bytes("<h2>Category.</h2>", "utf-8"))
        self.wfile.write(bytes("<p>Test.</p>", "utf-8"))
        self.wfile.write(bytes("<p>Test.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")