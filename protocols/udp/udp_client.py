import socket
import time

HOST = 'localhost' 
PORT = 6006

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    for i in range(1, 2):
        msg = f"UDP message {i}"
        print(f"[UDP CLIENT] Sending: {msg}")
        s.sendto(msg.encode(), (HOST, PORT))
        try:
            s.settimeout(2)
            data, _ = s.recvfrom(1024)
            print(f"[UDP CLIENT] Received: {data.decode()}")
        except socket.timeout:
            print(f"[UDP CLIENT] No response for message {i}")
        time.sleep(1)