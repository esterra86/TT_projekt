from utils.packet_utils import AppMessage


def build_http_get(path: str = "/") -> str:
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: example.local\r\n"
        f"User-Agent: TTProjekt-Simulator\r\n"
        f"\r\n"
    )
    return request


def build_http_response() -> str:
    body = "<html><body><h1>Hello from simulated HTTP server</h1></body></html>"
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
        f"{body}"
    )
    return response


def http_build_request_message(path: str = "/") -> AppMessage:
    data = build_http_get(path)
    return AppMessage(protocol="HTTP", data=data)


def http_handle_request_message(app_msg: AppMessage) -> AppMessage:
    """
    Serwer HTTP: przyjmuje AppMessage z żądaniem HTTP, zwraca AppMessage z odpowiedzią.
    """
    print("[HTTP] Otrzymano żądanie HTTP:")
    print(app_msg.data)
    response_data = build_http_response()
    print("[HTTP] Generuję odpowiedź HTTP 200 OK")
    return AppMessage(protocol="HTTP", data=response_data)