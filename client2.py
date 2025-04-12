# client2.py
import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(f"\nClient 1: {msg}")
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1',6666))

print("You are Client 2. Connected to server.")
threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

while True:
    msg = input("You: ")
    client.send(msg.encode())
