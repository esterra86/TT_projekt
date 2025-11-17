import socket

HOST = 'localhost'
PORT = 6006

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"[UDP SERVER] Listening on {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(1024)
        print(f"[UDP SERVER] Received from {addr}: {data.decode()}")
        s.sendto(data, addr)