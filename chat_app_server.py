import socket
import threading



clients_connected = []  # list for connected clients 


def handle_client(client, addr):
    
    print(f"Client Connected with address: {addr}")
   
    while True:
        try:
            msg = client.recv(1024)
            
            if not msg:
                break

            print(f"[{addr}] {msg.decode()}")

            # Relay message to the other client
            for c in clients_connected:
                if c != client:
                    c.send(msg)

        except:
           
            break

    print(f"Client Disconnected with Address: {addr}")
    
    if client in clients_connected:
        clients_connected.remove(client)
    client.close()





server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

port_num = 6666

ip = '127.0.0.1'

server_socket.bind((ip, port_num))

server_socket.listen(2)                       # cuurently for only 2 clients
 





while len(clients_connected) <2:

    print("\nwaiting for client")
    client_socket , client_address = server_socket.accept()

    
    print("\nSERVER CURRENTLY CONNECTED TO CLIENT WITH Address : ", client_address)
   
    clients_connected.append(client_socket)

    threading.Thread(target=handle_client, args=(client_socket , client_address )).start()





