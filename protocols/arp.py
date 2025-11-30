# protocols/arp.py

from layers.ethernet_layer import send, ETH_TYPE_ARP

# Symulacja lokalnego IP i MAC
LOCAL_IP = "192.168.0.10"
LOCAL_MAC = "AA:BB:CC:DD:EE:01"

# Prosty ARP cache: IP → MAC
arp_cache = {}


class ARPPacket:
    def __init__(self, opcode, sender_ip, sender_mac, target_ip, target_mac=None):
        self.opcode = opcode  # 1=request, 2=reply
        self.sender_ip = sender_ip
        self.sender_mac = sender_mac
        self.target_ip = target_ip
        self.target_mac = target_mac

    def __repr__(self):
        return (f"ARP(op={self.opcode}, sender={self.sender_ip}/{self.sender_mac}, "
                f"target={self.target_ip}/{self.target_mac})")


def resolve(ip):
    """
    Sprawdza cache; jeśli brak – wysyła ARP request.
    """
    if ip in arp_cache:
        print(f"[ARP] Cache hit: {ip} → {arp_cache[ip]}")
        return arp_cache[ip]

    print(f"[ARP] Cache miss dla {ip}, wysyłam ARP Request...")
    send_arp_request(ip)

    # W naszej symulacji zakładamy, że odpowiedź przyjdzie "magicznie"
    # (np. natychmiast po wywołaniu receive())
    if ip in arp_cache:
        return arp_cache[ip]

    print("[ARP] Brak odpowiedzi ARP!")
    return None


def send_arp_request(target_ip):
    """
    Buduje i wysyła ARP Request jako ramkę Ethernet broadcast.
    """
    arp = ARPPacket(
        opcode=1,
        sender_ip=LOCAL_IP,
        sender_mac=LOCAL_MAC,
        target_ip=target_ip,
        target_mac="00:00:00:00:00:00"
    )

    return send(arp, dst_mac="FF:FF:FF:FF:FF:FF", eth_type=ETH_TYPE_ARP)


def send_arp_reply(target_ip, target_mac):
    """
    Tworzy ARP Reply (odpowiedź).
    """
    arp = ARPPacket(
        opcode=2,
        sender_ip=LOCAL_IP,
        sender_mac=LOCAL_MAC,
        target_ip=target_ip,
        target_mac=target_mac
    )

    return send(arp, dst_mac=target_mac, eth_type=ETH_TYPE_ARP)


def handle_arp_packet(packet):
    """
    Obsługa odbioru pakietów ARP – request lub reply.
    """
    print(f"[ARP] Otrzymano pakiet: {packet}")

    # Jeśli ktoś pyta o nasz IP → wysyłamy odpowiedź
    if packet.opcode == 1 and packet.target_ip == LOCAL_IP:
        print("[ARP] Ktoś pyta o mój adres IP → wysyłam ARP Reply")
        arp_cache[packet.sender_ip] = packet.sender_mac
        send_arp_reply(packet.sender_ip, packet.sender_mac)

    # Jeśli otrzymaliśmy odpowiedź
    elif packet.opcode == 2:
        print(f"[ARP] Otrzymano ARP Reply: {packet.sender_ip} → {packet.sender_mac}")
        arp_cache[packet.sender_ip] = packet.sender_mac

    return packet
arp_cache["192.168.0.20"] = "66:55:44:33:22:11"
arp_cache["192.168.0.10"] = "AA:BB:CC:DD:EE:01"