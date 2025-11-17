# from http.server import HTTPServer, BaseHTTPRequestHandler
# import time

# HOST = "192.168.1.97" # run ipconfig in cmd and copy IPv4 Address from listed information
# PORT = 9999
# class NeuralHTTP(BaseHTTPRequestHandler):

#     #handles how we respond to get requests
#     def do_GET(self):
#         self.send_response(200)
#         #change content type to text-html
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#         self.wfile.write(bytes("<html><body><h1>Hello World</h1></body></html>", "utf-8"))

#     def do_POST(self):
#         self.send_response(200)
#         #we're gonna send json type of object
#         self.send_header("Content-type", "application/json")
#         self.end_headers()

#         date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
#         #time.time() - returns currnet time
#         self.wfile.write(bytes('{"time":"' +date + '" }', "utf-8"))




# server = HTTPServer((HOST,PORT), NeuralHTTP)
# print("server now running...")
#server.serve_forever()
#server.server_close()
#print("server stopped")


#in webbrowser paste 192.168.1.97:9999
#or in cmd curl 192.168.1.97:9999 (this will show you code in html)

from protocols.arp import resolve

if __name__ == "__main__":
    print("Test ARP:")
    mac = resolve("192.168.0.20")
    print("Otrzymany MAC:", mac)

from protocols.icmp import send_ping

if __name__ == "__main__":
    print("=== TEST ICMP PING ===")
    send_ping("192.168.0.20")

