# protocols/udp.py

class UDPSegment:
    """
    Uproszczona reprezentacja segmentu UDP.
    """
    def __init__(self, src_port, dst_port, payload):
        self.src_port = src_port
        self.dst_port = dst_port
        self.payload = payload  # tu może być np. zwykły string lub obiekt aplikacji

    def __repr__(self):
        return f"UDP(src_port={self.src_port}, dst_port={self.dst_port}, payload={self.payload})"


def handle_udp_segment(segment):
    """
    Prosta „aplikacja” UDP – na razie tylko logujemy, co przyszło.
    W przyszłości tu możesz przekazać dane do warstwy aplikacyjnej.
    """
    print(f"[UDP] Otrzymano segment: {segment}")
    print(f"[UDP] Dane aplikacji: {segment.payload}")
    # Można tu zwrócić np. odpowiedź, ale UDP nie wymaga odpowiedzi
    return segment