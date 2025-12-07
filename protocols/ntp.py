import time
from utils.packet_utils import AppMessage


def ntp_build_request() -> AppMessage:
    client_time = time.time()
    data = {
        "role": "client_request",
        "client_time": client_time,
    }
    return AppMessage(protocol="NTP", data=data)


def ntp_handle_request(app_msg: AppMessage) -> AppMessage:
    client_time = app_msg.data.get("client_time")
    server_time = time.time()
    print(f"[NTP] Otrzymano zapytanie NTP. client_time={client_time}")
    print(f"[NTP] server_time={server_time}")
    data = {
        "role": "server_response",
        "client_time": client_time,
        "server_time": server_time,
    }
    return AppMessage(protocol="NTP", data=data)


def ntp_handle_response(app_msg: AppMessage):
    client_time = app_msg.data.get("client_time")
    server_time = app_msg.data.get("server_time")
    print("[NTP] Otrzymano odpowiedź NTP:")
    print(f"  client_time = {client_time}")
    print(f"  server_time = {server_time}")
    diff = server_time - client_time
    print(f"  Różnica (server_time - client_time) = {diff} s")