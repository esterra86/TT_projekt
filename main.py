from protocols.arp import resolve
from protocols.icmp import send_ping
from layers.ethernet_layer import receive as eth_receive
from layers.transport_layer import send_udp_datagram
from protocols.tcp_sim import client_start_handshake

# funkcje warstwy aplikacyjnej – import dopiero tutaj, po innych warstwach
from layers.application_layer import (
    send_http_get,
    send_https_get,
    send_smtp_mail,
    send_ntp_query,
)


def test_arp():
    print("=== TEST 1: ARP (IP -> MAC) ===")
    mac = resolve("192.168.0.20")
    print("Otrzymany MAC:", mac)
    print()


def test_icmp_ping():
    print("=== TEST 2: ICMP PING (full round trip) ===")
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


def test_udp():
    print("=== TEST 3: UDP (symulowany) ===")
    # 1. Klient wysyła datagram UDP (UDP → IP → Ethernet)
    udp_frame = send_udp_datagram(
        dst_ip="192.168.0.20",
        src_port=5000,
        dst_port=6000,
        payload="Hello from UDP layer!",
    )

    print("\n--- Drugi host ODBIERA datagram UDP ---")
    # 2. „Drugi host” odbiera ramkę → Ethernet → IP → UDP
    if udp_frame is not None:
        eth_receive(udp_frame)
    else:
        print("[MAIN] Nie otrzymano ramki UDP (udp_frame is None)")
    print()


def test_tcp_handshake():
    print("=== TEST 4: TCP HANDSHAKE (symulowany) ===")
    client_ip = "192.168.0.10"
    server_ip = "192.168.0.20"
    client_port = 4000
    server_port = 80

    from protocols.tcp_sim import (
        client_start_handshake,
        server_handle_segment,
        client_handle_segment,
    )

    # 1. Klient inicjuje handshake: wysyła SYN (TCP → IP → Ethernet)
    tcp_client_state, syn_frame = client_start_handshake(
        dst_ip=server_ip,
        src_ip=client_ip,
        src_port=client_port,
        dst_port=server_port,
    )

    # SYN przeszedł przez IP i Ethernet – w ramce payloadem jest IPPacket
    print("\n--- Serwer ODBIERA SYN (IP z ramki) ---")
    syn_ip_packet = syn_frame.payload

    # 2. Serwer przetwarza SYN w tcp_sim.server_handle_segment → SYN-ACK
    tcp_server_state, syn_ack_frame = server_handle_segment(
        syn_ip_packet,
        conn_state=None,
    )

    # 3. Klient odbiera SYN-ACK (ramka z powrotem z IP/Ethernet)
    print("\n--- Klient ODBIERA SYN-ACK ---")
    if syn_ack_frame is None:
        print("[MAIN] Serwer nie wygenerował SYN-ACK – handshake przerwany")
        return

    syn_ack_ip_packet = syn_ack_frame.payload

    tcp_client_state, ack_frame = client_handle_segment(
        syn_ack_ip_packet,
        conn_state=tcp_client_state,
    )

    # 4. Serwer odbiera ACK i przechodzi do ESTABLISHED
    print("\n--- Serwer ODBIERA ACK ---")
    if ack_frame is None:
        print("[MAIN] Klient nie wygenerował ACK – handshake przerwany")
        return

    ack_ip_packet = ack_frame.payload

    tcp_server_state, _ = server_handle_segment(
        ack_ip_packet,
        conn_state=tcp_server_state,
    )

    print("\n[TCP_SIM] HANDSHAKE ZAKOŃCZONY")
    print("[TCP_SIM] Stan klienta:", tcp_client_state)
    print("[TCP_SIM] Stan serwera:", tcp_server_state)
    print()

def test_http():
    print("=== TEST 5: HTTP (symulowany, GET) ===")
    # HTTP bez TLS (HTTP → TCP → IP → Ethernet)
    http_frame = send_http_get("192.168.0.20", "/")
    print("\n--- Drugi host ODBIERA HTTP ---")
    eth_receive(http_frame)
    print()


def test_https():
    print("=== TEST 6: HTTPS (HTTP over TLS, symulowany) ===")
    https_frame = send_https_get("192.168.0.20", "/secure")
    print("\n--- Drugi host ODBIERA HTTPS ---")
    eth_receive(https_frame)
    print()


def test_smtp():
    print("=== TEST 7: SMTP (symulowany) ===")
    smtp_frame = send_smtp_mail(
        dst_ip="192.168.0.20",
        sender="emilia.jerdanek@gmail.com",
        recipient="marta.zelasko@gmail.com",
        body="Hello world!",
        use_tls=False,
    )
    print("\n--- Drugi host ODBIERA SMTP ---")
    eth_receive(smtp_frame)
    print()


def test_smtps():
    print("=== TEST 8: SMTPS (SMTP over TLS, symulowany) ===")
    smtps_frame = send_smtp_mail(
        dst_ip="192.168.0.20",
        sender="emilia.jerdanek@gmail.com",
        recipient="marta.zelasko@gmail.com",
        body="Hello!",
        use_tls=True,
    )
    print("\n--- Drugi host ODBIERA SMTPS ---")
    eth_receive(smtps_frame)
    print()


def test_ntp():
    print("=== TEST 9: NTP (symulowany) ===")
    ntp_frame = send_ntp_query("192.168.0.20")
    print("\n--- Drugi host ODBIERA NTP ---")
    eth_receive(ntp_frame)
    print()


if __name__ == "__main__":
    test_arp()
    test_icmp_ping()
    test_udp()
    test_tcp_handshake()
    test_http()
    test_https()
    test_smtp()
    test_smtps()
    test_ntp()