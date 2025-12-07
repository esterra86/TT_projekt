from utils.packet_utils import AppMessage
from protocols.http import http_build_request_message, http_handle_request_message
from protocols.smtp import smtp_build_message, smtp_handle_message
from protocols.ntp import ntp_build_request, ntp_handle_request, ntp_handle_response
from protocols.tls import tls_wrap, tls_unwrap


# ===== WYCHODZĄCE (klient) =====

def send_http_get(dst_ip: str, path: str = "/"):
    """
    HTTP bez TLS, przez TCP.
    Zwraca ramkę Ethernet.
    """
    from layers.transport_layer import send_tcp_segment_wrapper

    # Tworzymy AppMessage z żądaniem HTTP
    app_msg = http_build_request_message(path)
    # Wysyłamy AppMessage jako payload TCP
    frame = send_tcp_segment_wrapper(
        dst_ip=dst_ip,
        src_port=5001,
        dst_port=80,
        payload=app_msg,   # <==== WAŻNE: AppMessage, nie string
    )
    return frame


def send_https_get(dst_ip: str, path: str = "/"):
    """
    HTTP przez TLS, przez TCP.
    Zwraca ramkę Ethernet.
    """
    from layers.transport_layer import send_tcp_segment_wrapper

    # HTTP request jako AppMessage
    app_msg = http_build_request_message(path)
    # Zawijamy w TLS → dostajemy AppMessage(protocol="TLS-HTTP", data=zaszyfrowany tekst)
    tls_msg = tls_wrap(app_msg)

    frame = send_tcp_segment_wrapper(
        dst_ip=dst_ip,
        src_port=5002,
        dst_port=443,
        payload=tls_msg,   # <==== AppMessage TLS-HTTP
    )
    return frame


def send_smtp_mail(dst_ip: str, sender: str, recipient: str, body: str, use_tls: bool = False):
    from layers.transport_layer import send_tcp_segment_wrapper

    app_msg = smtp_build_message(sender, recipient, body)
    if use_tls:
        # Zawijamy w TLS → AppMessage(protocol="TLS-SMTP", data=...)
        app_msg = tls_wrap(app_msg)
        dst_port = 465
        src_port = 6002
    else:
        dst_port = 25
        src_port = 6001

    frame = send_tcp_segment_wrapper(
        dst_ip=dst_ip,
        src_port=src_port,
        dst_port=dst_port,
        payload=app_msg,   # <==== AppMessage (SMTP lub TLS-SMTP)
    )
    return frame


def send_ntp_query(dst_ip: str):
    """
    NTP po UDP – ramka Ethernet jako wynik.
    """
    from layers.transport_layer import send_udp_datagram

    app_msg = ntp_build_request()
    # W UDP na razie wysyłamy słownik (data AppMessage) jako payload,
    # bo Twój UDP jest bardzo prosty; można by też przesłać AppMessage.
    frame = send_udp_datagram(
        dst_ip=dst_ip,
        src_port=7000,
        dst_port=123,
        payload=app_msg.data,
    )
    return frame


# ===== PRZYCHODZĄCE (serwer / odbiorca) =====

def receive_app_message(app_msg: AppMessage):
    """
    Wołane z warstwy transportowej, gdy dotarliśmy do warstwy aplikacji.
    Rozpoznaje protokół i wykonuje odpowiednią logikę.
    """
    proto = app_msg.protocol

    # TLS rozpakowujemy, a potem wywołujemy ponownie to samo wejście.
    if proto.startswith("TLS-"):
        inner = tls_unwrap(app_msg)
        return receive_app_message(inner)

    if proto == "HTTP":
        reply = http_handle_request_message(app_msg)
        print("[APP] HTTP odpowiedź (logiczna):")
        print(reply.data)
        return

    if proto == "SMTP":
        reply = smtp_handle_message(app_msg)
        print("[APP] SMTP odpowiedź (logiczna):", reply.data)
        return

    if proto == "NTP":
        role = app_msg.data.get("role")
        if role == "client_request":
            reply = ntp_handle_request(app_msg)
            print("[APP] NTP serwer wygenerował odpowiedź logiczną.")
            ntp_handle_response(reply)  # dla uproszczenia od razu "po stronie klienta"
        elif role == "server_response":
            ntp_handle_response(app_msg)
        else:
            print("[APP] NTP: nieznana rola:", role)
        return

    print("[APP] Nieznany protokół aplikacyjny:", proto)