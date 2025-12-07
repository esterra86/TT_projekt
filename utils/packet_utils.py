from dataclasses import dataclass
from typing import Any


@dataclass
class UDPSegment:
    src_port: int
    dst_port: int
    payload: Any

    def __repr__(self) -> str:
        return f"UDPSegment({self.src_port}->{self.dst_port}, payload={self.payload})"


@dataclass
class TCPSegment:
    src_port: int
    dst_port: int
    seq: int
    ack: int
    flags: str  # np. "SYN", "SYN-ACK", "ACK", "PSH-ACK"
    payload: Any = None

    def __repr__(self) -> str:
        return (f"TCPSegment({self.src_port}->{self.dst_port}, seq={self.seq}, "
                f"ack={self.ack}, flags={self.flags}, payload={self.payload})")


@dataclass
class AppMessage:
    protocol: str  # "HTTP", "SMTP", "NTP", "TLS-HTTP", itp.
    data: Any

    def __repr__(self) -> str:
        return f"AppMessage(protocol={self.protocol}, data_len={len(str(self.data))})"