# layers/ethernet_layer.py

from protocols.arp import handle_arp_packet

ETH_TYPE_IP = 0x0800
ETH_TYPE_ARP = 0x0806


class EthernetFrame:
    def __init__(self, src_mac, dst_mac, eth_type, payload, crc=0xFFFF):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.eth_type = eth_type
        self.payload = payload
        self.crc = crc

    def __repr__(self):
        return (f"EthernetFrame(src={self.src_mac}, dst={self.dst_mac}, "
                f"type={hex(self.eth_type)}, payload={self.payload})")


# Symulacja lokalnego MAC karty sieciowej
LOCAL_MAC = "AA:BB:CC:DD:EE:01"


def send(payload, dst_mac, eth_type):
    """
    Tworzy i zwraca ramkę Ethernet.
    (W prawdziwej sieci byłaby tu funkcja wysyłająca ramkę do medium.)
    """
    frame = EthernetFrame(
        src_mac=LOCAL_MAC,
        dst_mac=dst_mac,
        eth_type=eth_type,
        payload=payload,
        crc=0xFFFF
    )
    print(f"[Ethernet] WYSLANO ramkę: {frame}")
    return frame


def receive(frame):
    """
    Odbiór ramki – decyduje, co robić w zależności od eth_type.
    """
    print(f"[Ethernet] ODEBRANO ramkę: {frame}")

    if frame.eth_type == ETH_TYPE_ARP:
        return handle_arp_packet(frame.payload)

    elif frame.eth_type == ETH_TYPE_IP:
        # W kroku 3 podłączymy tu ip_layer.receive()
        print("[Ethernet] Przekazano do warstwy IP")
        return frame.payload

    else:
        print("[Ethernet] Nieznany typ ramki")
