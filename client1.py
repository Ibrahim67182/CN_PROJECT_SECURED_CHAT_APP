import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"\nFriend: {message}\nYou: ", end='')
        except:
            print("\n[!] Connection closed by server.")
            break

def main():
    server_ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    server_port = 6666

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    print("[+] Connected to server!")

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        msg = input("You: ")
        if msg.lower() == "exit":
            break
        client_socket.send(msg.encode())

    client_socket.close()

if __name__ == "__main__":
    main()
