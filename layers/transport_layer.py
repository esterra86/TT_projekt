from typing import Optional

from layers.ip_layer import send as ip_send
from protocols.udp import UDPSegment, handle_udp_segment
from protocols.tcp_sim import TCPSegment as TCP_Segment_Class
from layers.application_layer import receive_app_message
from utils.packet_utils import AppMessage

LOCAL_IP = "192.168.0.10"


def send_udp_datagram(dst_ip: str, src_port: int, dst_port: int, payload):
    """
    Tworzy UDPSegment, przekazuje go do warstwy IP (która zrobi ARP + Ethernet)
    i zwraca ramkę Ethernet.
    `payload` może być stringiem lub innym obiektem (np. dict dla NTP).
    """
    udp_seg = UDPSegment(src_port=src_port, dst_port=dst_port, payload=payload)
    print(f"[UDP] WYSLANO segment: {udp_seg}")

    frame = ip_send(udp_seg, dst_ip=dst_ip, proto="UDP")
    return frame


def send_tcp_segment_wrapper(dst_ip: str, src_port: int, dst_port: int, payload):
    """
    Uproszczony helper: tworzy segment TCP z danymi aplikacyjnymi
    i wysyła go przez warstwę IP (po ustanowionym handshake).
    `payload` to teraz zwykle AppMessage (HTTP / SMTP / TLS-HTTP / TLS-SMTP).
    """
    seg = TCP_Segment_Class(
        src_port=src_port,
        dst_port=dst_port,
        seq=1,
        ack=0,
        flags=set(),  # brak flag sterujących – segment danych
        payload=payload,
    )
    print(f"[TCP] WYSLANO segment: {seg}")
    frame = ip_send(seg, dst_ip=dst_ip, proto="TCP")
    return frame


def receive(ip_packet, tcp_role: Optional[str] = None, tcp_conn_state=None):
    """
    Odbiór IPPacket w warstwie transportowej:
    - dla UDP: woła handle_udp_segment, a jeśli payload wygląda na dane aplikacji, loguje je;
    - dla TCP: jeśli payload to AppMessage, przekazuje go do application_layer.
    Zwraca payload (UDPSegment/TCPSegment) dla IP jako ewentualną odpowiedź (tu zwykle None).
    """
    if ip_packet.proto == "UDP":
        seg = ip_packet.payload
        print(f"[UDP] ODEBRANO segment: {seg}")

        reply_seg = handle_udp_segment(seg)

        # Jeśli payload jest AppMessage (tego nie używamy teraz, ale zostawiamy możliwość)
        if isinstance(reply_seg.payload, AppMessage):
            receive_app_message(reply_seg.payload)

        return None

    elif ip_packet.proto == "TCP":
        seg = ip_packet.payload
        print(f"[TCP] ODEBRANO segment (poza handshake): {seg}")

        # Oczekujemy AppMessage w payload (HTTP/SMTP/TLS-HTTP/TLS-SMTP)
        if isinstance(seg.payload, AppMessage):
            receive_app_message(seg.payload)
        else:
            # Gdyby kiedyś pojawił się zwykły string:
            print("[TCP] Payload nie jest AppMessage – pomijam warstwę aplikacji.")

        return None

    else:
        print(f"[TRANSPORT] Nieznany protokół: {ip_packet.proto}")
        return None