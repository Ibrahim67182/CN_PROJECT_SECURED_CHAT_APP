import socket
import threading

# Store all connected clients
clients_connected = []

# Function to handle communication with each client
def handle_client(client_socket, client_address):
    print(f"[+] Client connected: {client_address}")

    while True:
        try:
            message = client_socket.recv(1024)

            if not message:
                break  # Client closed connection

            print(f"[{client_address}] {message.decode()}")

            # Broadcast to all other clients
            for client in clients_connected:
                if client != client_socket:
                    client.send(message)

        except Exception as e:
            print(f"[-] Error with {client_address}: {e}")
            break

    # Remove client on disconnect
    print(f"[-] Client disconnected: {client_address}")
    if client_socket in clients_connected:
        clients_connected.remove(client_socket)
    client_socket.close()

# Main server function
def start_server(server_ip="127.0.0.1", port=6666, max_clients=5):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((server_ip, port))
    except Exception as e:
        print(f"[-] Failed to bind server: {e}")
        return

    server_socket.listen(max_clients)
    print(f"[+] Server started on {server_ip}:{port}. Waiting for clients...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[+] Connection from {client_address}")

        clients_connected.append(client_socket)

        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    # For testing locally on SAME device use '127.0.0.1'
    # Later, for 2 devices, set it to your server machine IP like '192.168.0.5'
    
    HOST = "127.0.0.1"   # <-- Change this to your server IP when needed
    PORT = 6666

    start_server(server_ip=HOST, port=PORT)
