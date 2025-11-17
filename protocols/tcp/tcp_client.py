import socket
import time

HOST = '127.0.0.1'
PORT = 6000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for i in range(1, 10):
        msg = f"TCP message {i}"
        print(f"[TCP CLIENT] Sending: {msg}")
        s.sendall(msg.encode())
        data = s.recv(1024)
        print(f"[TCP CLIENT] Received: {data.decode()}")
        time.sleep(1)



        