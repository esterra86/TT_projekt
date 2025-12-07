from utils.packet_utils import AppMessage

_TLS_KEY = 5  # uproszczony "klucz"


def _simple_encrypt(text: str) -> str:
    return "".join(chr((ord(c) + _TLS_KEY) % 65536) for c in text)


def _simple_decrypt(text: str) -> str:
    return "".join(chr((ord(c) - _TLS_KEY) % 65536) for c in text)


def tls_wrap(app_msg: AppMessage) -> AppMessage:
    plain = str(app_msg.data)
    encrypted = _simple_encrypt(plain)
    new_protocol = f"TLS-{app_msg.protocol}"
    print(f"[TLS] Szyfruję dane protokołu {app_msg.protocol}. Długość: {len(plain)}")
    return AppMessage(protocol=new_protocol, data=encrypted)


def tls_unwrap(app_msg: AppMessage) -> AppMessage:
    if not app_msg.protocol.startswith("TLS-"):
        return app_msg

    inner_proto = app_msg.protocol.replace("TLS-", "", 1)
    encrypted = app_msg.data
    decrypted = _simple_decrypt(encrypted)
    print(f"[TLS] Deszyfruję dane protokołu {inner_proto}. Długość: {len(decrypted)}")
    return AppMessage(protocol=inner_proto, data=decrypted)