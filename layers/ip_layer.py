# layers/ip_layer.py

from layers.ethernet_layer import send as eth_send, ETH_TYPE_IP
from protocols.arp import resolve


class IPPacket:
    def __init__(self, src_ip, dst_ip, ttl, packet_id, payload):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.packet_id = packet_id
        self.payload = payload

    def __repr__(self):
        return (f"IP(src={self.src_ip}, dst={self.dst_ip}, "
                f"ttl={self.ttl}, id={self.packet_id}, payload={self.payload})")


LOCAL_IP = "192.168.0.10"
PACKET_ID_COUNTER = 0


def send(payload, dst_ip):
    """
    Tworzy pakiet IP, znajduje MAC docelowy przez ARP,
    i wysyła przez warstwę Ethernet.
    """

    global PACKET_ID_COUNTER
    PACKET_ID_COUNTER += 1

    # najpierw ARP — bez tego nie wyślemy ramki
    mac = resolve(dst_ip)
    if mac is None:
        print("[IP] Nie udało się rozwiązać MAC — przerwano wysyłanie")
        return None

    ip_packet = IPPacket(
        src_ip=LOCAL_IP,
        dst_ip=dst_ip,
        ttl=64,
        packet_id=PACKET_ID_COUNTER,
        payload=payload
    )

    print(f"[IP] Wysyłam pakiet IP: {ip_packet}")
    return eth_send(ip_packet, mac, ETH_TYPE_IP)


def receive(ip_packet):
    """
    Odbiera pakiet IP i przekazuje dalej do odpowiedniego protokołu.
    """
    print(f"[IP] Otrzymano pakiet IP: {ip_packet}")

    # rozpoznawanie typu pakietu (ICMP w payload)
    from protocols.icmp import handle_icmp_packet

    payload = ip_packet.payload

    # ICMP
    if hasattr(payload, "type"):  # prosty sposób wykrycia ICMP
        return handle_icmp_packet(ip_packet)

    print("[IP] Nieznany protokół IP")
