from utils.packet_utils import AppMessage


def build_smtp_conversation(sender: str, recipient: str, body: str) -> str:
    lines = [
        f"MAIL FROM:<{sender}>",
        f"RCPT TO:<{recipient}>",
        "DATA",
        body,
        ".",  # koniec DATA
    ]
    return "\r\n".join(lines) + "\r\n"


def smtp_build_message(sender: str, recipient: str, body: str) -> AppMessage:
    data = build_smtp_conversation(sender, recipient, body)
    return AppMessage(protocol="SMTP", data=data)


def smtp_handle_message(app_msg: AppMessage) -> AppMessage:
    print("[SMTP] Otrzymano wiadomość SMTP:")
    print(app_msg.data)
    response = "250 OK: message accepted for delivery"
    print("[SMTP] Odpowiedź serwera:", response)
    return AppMessage(protocol="SMTP", data=response)