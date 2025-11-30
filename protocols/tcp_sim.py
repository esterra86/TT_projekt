# protocols/tcp_sim.py

from layers.ip_layer import send as ip_send


class TCPSegment:
    """
    Uproszczona reprezentacja segmentu TCP w symulatorze.
    flags: zbiór stringów, np. {"SYN"}, {"SYN", "ACK"}, {"ACK"}
    """
    def __init__(self, src_port, dst_port, seq, ack, flags=None, payload=""):
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq = seq
        self.ack = ack
        self.flags = flags or set()
        self.payload = payload

    def __repr__(self):
        flags_str = ",".join(sorted(self.flags)) if self.flags else "-"
        return (f"TCP(src_port={self.src_port}, dst_port={self.dst_port}, "
                f"seq={self.seq}, ack={self.ack}, flags={flags_str}, "
                f"payload='{self.payload}')")


class TCPConnectionState:
    """
    Bardzo uproszczony stan połączenia TCP (po jednej stronie).
    """
    def __init__(self, role, src_ip, dst_ip, src_port, dst_port):
        self.role = role              # "client" lub "server"
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.state = "CLOSED"
        self.seq = 100  # startowa wartość sekwencji (dla prostoty stała)
        self.ack = 0

    def __repr__(self):
        return (f"TCPConnectionState(role={self.role}, state={self.state}, "
                f"{self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port}, "
                f"seq={self.seq}, ack={self.ack})")


def client_start_handshake(dst_ip, src_ip, src_port, dst_port):
    """
    Klient inicjuje połączenie TCP: wysyła SYN.
    Zwraca (conn_state, frame), gdzie frame to ramka Ethernet.
    """
    conn = TCPConnectionState(
        role="client",
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=src_port,
        dst_port=dst_port,
    )

    print(f"[TCP_SIM CLIENT] Stan początkowy: {conn}")

    # Przejście do SYN_SENT
    conn.state = "SYN_SENT"

    syn_segment = TCPSegment(
        src_port=src_port,
        dst_port=dst_port,
        seq=conn.seq,
        ack=0,
        flags={"SYN"},
        payload=""
    )

    print(f"[TCP_SIM CLIENT] Wysyłam SYN: {syn_segment}")
    frame = ip_send(syn_segment, dst_ip, proto="TCP")
    return conn, frame


def server_handle_segment(ip_packet, conn_state=None):
    """
    Serwer odbiera segment TCP i odpowiada zgodnie z logiką:
    - jeśli SYN → stan LISTEN -> SYN_RECEIVED, wysyła SYN-ACK
    - jeśli ACK → stan SYN_RECEIVED -> ESTABLISHED

    Zwraca (nowy_conn_state, frame_odpowiedzi_lub_None)
    """
    segment = ip_packet.payload
    print(f"[TCP_SIM SERVER] Otrzymano segment: {segment}")

    # Jeśli nie mamy jeszcze stanu połączenia po stronie serwera — tworzymy go na podstawie pierwszego segmentu (SYN)
    if conn_state is None:
        conn_state = TCPConnectionState(
            role="server",
            src_ip=ip_packet.dst_ip,   # serwer
            dst_ip=ip_packet.src_ip,   # klient
            src_port=segment.dst_port,
            dst_port=segment.src_port,
        )
        conn_state.state = "LISTEN"

    print(f"[TCP_SIM SERVER] Aktualny stan: {conn_state}")

    # Obsługa SYN
    if "SYN" in segment.flags and conn_state.state == "LISTEN":
        print("[TCP_SIM SERVER] Odebrano SYN → przejście do SYN_RECEIVED, wysyłam SYN-ACK")
        conn_state.state = "SYN_RECEIVED"
        # Ustawiamy własną sekwencję i ack
        conn_state.seq = 200
        conn_state.ack = segment.seq + 1

        syn_ack_segment = TCPSegment(
            src_port=conn_state.src_port,
            dst_port=conn_state.dst_port,
            seq=conn_state.seq,
            ack=conn_state.ack,
            flags={"SYN", "ACK"},
            payload=""
        )

        print(f"[TCP_SIM SERVER] Wysyłam SYN-ACK: {syn_ack_segment}")
        frame = ip_send(syn_ack_segment, conn_state.dst_ip, proto="TCP")
        return conn_state, frame

    # Obsługa ACK po SYN-ACK
    if "ACK" in segment.flags and conn_state.state == "SYN_RECEIVED":
        print("[TCP_SIM SERVER] Odebrano ACK → połączenie ESTABLISHED")
        conn_state.state = "ESTABLISHED"
        conn_state.ack = segment.seq + 1
        print(f"[TCP_SIM SERVER] Stan po ustanowieniu połączenia: {conn_state}")
        return conn_state, None

    print("[TCP_SIM SERVER] Segment nie pasuje do spodziewanego etapu handshake")
    return conn_state, None


def client_handle_segment(ip_packet, conn_state):
    """
    Klient odbiera segment TCP w trakcie handshake:
    - jeśli SYN-ACK w stanie SYN_SENT → wysyła ACK i przechodzi do ESTABLISHED

    Zwraca (nowy_conn_state, frame_odpowiedzi_lub_None)
    """
    segment = ip_packet.payload
    print(f"[TCP_SIM CLIENT] Otrzymano segment: {segment}")
    print(f"[TCP_SIM CLIENT] Aktualny stan: {conn_state}")

    # Oczekujemy SYN-ACK
    if conn_state.state == "SYN_SENT" and {"SYN", "ACK"} <= segment.flags:
        print("[TCP_SIM CLIENT] Odebrano SYN-ACK → wysyłam ACK, stan ESTABLISHED")
        conn_state.state = "ESTABLISHED"
        conn_state.ack = segment.seq + 1
        conn_state.seq += 1  # potwierdzamy wysłanego SYN-a

        ack_segment = TCPSegment(
            src_port=conn_state.src_port,
            dst_port=conn_state.dst_port,
            seq=conn_state.seq,
            ack=conn_state.ack,
            flags={"ACK"},
            payload=""
        )

        print(f"[TCP_SIM CLIENT] Wysyłam ACK: {ack_segment}")
        frame = ip_send(ack_segment, conn_state.dst_ip, proto="TCP")
        return conn_state, frame

    print("[TCP_SIM CLIENT] Segment nie pasuje do spodziewanego SYN-ACK")
    return conn_state, None