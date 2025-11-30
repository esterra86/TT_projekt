# protocols/icmp.py

from layers.ip_layer import send as ip_send

# ICMP typy
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0

ECHO_ID = 0


class ICMPPacket:
    def __init__(self, type, code, identifier, seq, payload=""):
        self.type = type
        self.code = code
        self.identifier = identifier
        self.seq = seq
        self.payload = payload

    def __repr__(self):
        return (f"ICMP(type={self.type}, code={self.code}, id={self.identifier}, "
                f"seq={self.seq}, payload='{self.payload}')")


def send_ping(dst_ip):
    """
    Wysyła ICMP Echo Request (PING).
    """
    global ECHO_ID
    ECHO_ID += 1

    packet = ICMPPacket(
        type=ICMP_ECHO_REQUEST,
        code=0,
        identifier=ECHO_ID,
        seq=1,
        payload="HELLO!"
    )

    print(f"[ICMP] Wysyłam Echo Request do {dst_ip}")
    return ip_send(packet, dst_ip, proto="ICMP")


def handle_icmp_packet(ip_packet):
    """
    Obsługa odbioru pakietów ICMP.
    """
    icmp = ip_packet.payload

    print(f"[ICMP] Otrzymano: {icmp}")

    # jeśli to Echo Request → odeślij Reply
    if icmp.type == ICMP_ECHO_REQUEST:
        print("[ICMP] To Echo Request → odpowiadam Echo Reply")

        reply = ICMPPacket(
            type=ICMP_ECHO_REPLY,
            code=0,
            identifier=icmp.identifier,
            seq=icmp.seq,
            payload=icmp.payload
        )

        return ip_send(reply, ip_packet.src_ip, proto="ICMP")

    # jeśli to Echo Reply
    elif icmp.type == ICMP_ECHO_REPLY:
        print("[ICMP] Otrzymano Echo Reply!")
        return icmp

    else:
        print("[ICMP] Nieznany typ ICMP")
