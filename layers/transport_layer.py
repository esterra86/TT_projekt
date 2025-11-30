# layers/transport_layer.py

from protocols.udp import UDPSegment, handle_udp_segment
from protocols.tcp_sim import server_handle_segment, client_handle_segment
from layers.ip_layer import send as ip_send, IPPacket


def send_udp_datagram(dst_ip, src_port, dst_port, payload):
    """
    Tworzy segment UDP i wysyła go przez warstwę IP.
    Zwraca ramkę Ethernet, podobnie jak send_ping (ICMP).
    """
    segment = UDPSegment(src_port=src_port, dst_port=dst_port, payload=payload)
    print(f"[Transport] Wysyłam datagram UDP do {dst_ip}: {segment}")
    return ip_send(segment, dst_ip, proto="UDP")


def receive(ip_packet, tcp_role=None, tcp_conn_state=None):
    """
    Odbiera pakiet IP i na podstawie ip_packet.proto
    przekazuje go do odpowiedniego protokołu transportowego (UDP/TCP).

    Dla TCP używamy dodatkowych parametrów:
    - tcp_role: 'client' lub 'server'
    - tcp_conn_state: aktualny stan połączenia TCP
    """
    print(f"[Transport] Otrzymano pakiet IP w warstwie transportowej: {ip_packet}")

    if ip_packet.proto == "UDP":
        segment = ip_packet.payload
        return handle_udp_segment(segment)

    elif ip_packet.proto == "TCP":
        if tcp_role == "server":
            return server_handle_segment(ip_packet, tcp_conn_state)
        elif tcp_role == "client":
            if tcp_conn_state is None:
                print("[Transport] Brak stanu połączenia TCP po stronie klienta")
                return None
            return client_handle_segment(ip_packet, tcp_conn_state)
        else:
            print("[Transport] Nie podano roli dla TCP (client/server)")
            return None

    else:
        print(f"[Transport] Nieznany protokół transportowy: {ip_packet.proto}")
        return None