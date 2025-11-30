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
from protocols.icmp import send_ping
from layers.ethernet_layer import receive as eth_receive
from layers.transport_layer import send_udp_datagram
from protocols.tcp_sim import client_start_handshake


if __name__ == "__main__":
    # === TEST ARP ===
    print("=== TEST ARP ===")
    mac = resolve("192.168.0.20")
    print("Otrzymany MAC:", mac)
    print()

    # === TEST ICMP PING (full round trip) ===
    print("=== TEST ICMP PING (full round trip) ===")
    # 1. Klient wysyła Echo Request (ICMP → IP → Ethernet)
    req_frame = send_ping("192.168.0.20")

    print("\n--- Drugi host ODBIERA Echo Request ---")
    # 2. „Drugi host” odbiera ramkę → Ethernet → IP → ICMP (generuje Echo Reply)
    reply_frame = eth_receive(req_frame)

    print("\n--- Pierwszy host ODBIERA Echo Reply ---")
    # 3. „Pierwszy host” odbiera Echo Reply (Ethernet → IP → ICMP)
    if reply_frame is not None:
        eth_receive(reply_frame)
    else:
        print("[MAIN] Nie otrzymano ramki z Echo Reply")
    print()

    # === TEST UDP (symulowany) ===
    print("=== TEST UDP (symulowany) ===")
    # 1. Klient wysyła datagram UDP (UDP → IP → Ethernet)
    udp_frame = send_udp_datagram(
        dst_ip="192.168.0.20",
        src_port=5000,
        dst_port=6000,
        payload="Hello from UDP layer!"
    )

    print("\n--- Drugi host ODBIERA datagram UDP ---")
    # 2. „Drugi host” odbiera ramkę → Ethernet → IP → Transport (UDP)
    if udp_frame is not None:
        eth_receive(udp_frame)
    else:
        print("[MAIN] Nie otrzymano ramki UDP (udp_frame is None)")
    print()

    # === TEST TCP HANDSHAKE (symulowany) ===
    print("=== TEST TCP HANDSHAKE (symulowany) ===")
    client_ip = "192.168.0.10"
    server_ip = "192.168.0.20"
    client_port = 4000
    server_port = 80

    # 1. Klient inicjuje handshake: wysyła SYN (TCP → IP → Ethernet)
    tcp_client_state, syn_frame = client_start_handshake(
        dst_ip=server_ip,
        src_ip=client_ip,
        src_port=client_port,
        dst_port=server_port
    )

    # Na potrzeby testu nie przepuszczamy SYN przez ip_layer.receive,
    # tylko bierzemy IPPacket bezpośrednio z payloadu ramki.
    print("\n--- Serwer ODBIERA SYN (bezpośrednio IP z ramki) ---")
    syn_ip_packet = syn_frame.payload

    from layers.transport_layer import receive as transport_receive

    # 2. Serwer przetwarza SYN w warstwie transportowej → SYN-ACK
    tcp_server_state, syn_ack_frame = transport_receive(
        syn_ip_packet,
        tcp_role="server",
        tcp_conn_state=None
    )

    # 3. Klient odbiera SYN-ACK (ponownie, bierzemy IPPacket z ramki)
    print("\n--- Klient ODBIERA SYN-ACK ---")
    syn_ack_ip_packet = syn_ack_frame.payload

    tcp_client_state, ack_frame = transport_receive(
        syn_ack_ip_packet,
        tcp_role="client",
        tcp_conn_state=tcp_client_state
    )

    # 4. Serwer odbiera ACK i przechodzi do ESTABLISHED
    print("\n--- Serwer ODBIERA ACK ---")
    ack_ip_packet = ack_frame.payload

    tcp_server_state, _ = transport_receive(
        ack_ip_packet,
        tcp_role="server",
        tcp_conn_state=tcp_server_state
    )

    print("\n[TCP_SIM] HANDSHAKE ZAKOŃCZONY")
    print("[TCP_SIM] Stan klienta:", tcp_client_state)
    print("[TCP_SIM] Stan serwera:", tcp_server_state)