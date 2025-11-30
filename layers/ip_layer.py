# layers/ip_layer.py

from layers.ethernet_layer import send as eth_send, ETH_TYPE_IP
from protocols.arp import resolve
import random

class IPPacket:
    def __init__(self, src_ip, dst_ip, ttl, packet_id, proto, payload):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.packet_id = packet_id
        self.proto = proto      # 'ICMP', 'TCP', 'UDP'
        self.payload = payload

    def __repr__(self):
        return (f"IP(src={self.src_ip}, dst={self.dst_ip}, "
                f"ttl={self.ttl}, id={self.packet_id}, proto={self.proto}, "
                f"payload={self.payload})")

LOCAL_IP = "192.168.0.10"
PACKET_ID_COUNTER = 0

def send(payload, dst_ip, proto="ICMP"):
    """
    Tworzy pakiet IP, znajduje MAC docelowy przez ARP,
    i wysyła przez warstwę Ethernet.
    `proto` określa protokół warstwy wyższej: 'ICMP', 'UDP', 'TCP'.
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
        proto=proto,
        payload=payload
    )

    print(f"[IP] Wysyłam pakiet IP: {ip_packet}")
    return eth_send(ip_packet, mac, ETH_TYPE_IP)


PACKET_LOSS_PROBABILITY = 0.0 

def receive(ip_packet):
    """
    Odbiera pakiet IP i przekazuje dalej do odpowiedniego protokołu.
    """
    print(f"[IP] Otrzymano pakiet IP: {ip_packet}")

    # 1. Symulacja utraty pakietu
    if random.random() < PACKET_LOSS_PROBABILITY:
        print("[IP] Pakiet zgubiony (symulacja utraty pakietu)")
        return None

    # 2. Decrement TTL
    ip_packet.ttl -= 1
    if ip_packet.ttl <= 0:
        print("[IP] TTL = 0 → pakiet odrzucony (czas życia skończony)")
        # Tu w przyszłości można wygenerować ICMP Time Exceeded
        return None

 # 3. Dispatch na podstawie ip_packet.proto
    if ip_packet.proto == "ICMP":
        from protocols.icmp import handle_icmp_packet
        return handle_icmp_packet(ip_packet)

    else:
        # Dla wszystkiego innego (UDP, TCP, ...) idziemy do warstwy transportowej
        from layers.transport_layer import receive as transport_receive
        return transport_receive(ip_packet)