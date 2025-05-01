import socket
import threading
import time

clients = {}  # {client_name: client_socket}
groups = {}  # {creator: creator_name ,  members : [member1, member2 , ......]}

# ----------------------------------------------------broadcasting-----------------------------------------
def broadcast_message(message, sender=None):
    """Send a message to all clients except sender."""
    for name, client_socket in clients.items():
        if name != sender:
            try:
                client_socket.send(message.encode())
            except:
                print("\n[!] Error broadcasting the message to", name)

# ----------------------------------------------------selective broadcast------------------------------
def selective_broadcast(message, target_list, sender=None):
    """Send a message to selected clients only."""
    for target_name in target_list:
        if target_name in clients and target_name != sender:
            try:
                clients[target_name].send(message.encode())
            except:
                print(f"\n[!] Error sending selective broadcast to {target_name}")

# ------------------------------------------------group message functions -------------------------------------
def send_group_message(group_name, sender, message):
    """Send message to all members of a group."""
    if group_name not in groups:
        return f"\n[!] Group '{group_name}' does not exist."
    if sender not in groups[group_name]["members"]:
        return "\n[!] You are not a member of this group."
    for member in groups[group_name]["members"]:
        if member != sender and member in clients:
            try:
                clients[member].send(f"[Group:{group_name}] {sender}: {message}".encode())
            except:
                print(f"\n[!] Error sending group message to {member}")
    return "\nMessage sent to group."

def create_group(group_name, creator, members):
    """Create a new group with validation."""
    if group_name in groups:
        return "\n[!] Group already exists."
    for member in members:
        if member not in clients:
            return f"\n[!] User '{member}' not found. Please add only connected users."
    groups[group_name] = {"creator": creator, "members": list(set(members + [creator]))}
    return f"\n[+] Group '{group_name}' created successfully with members: {', '.join(groups[group_name]['members'])}"

def remove_member(group_name, remover, member_to_remove):
    """Remove a member from a group (only by creator)."""
    if group_name not in groups:
        return "\n[!] Group not found."
    if groups[group_name]["creator"] != remover:
        return "\n[!] Only group creator can remove members."
    if member_to_remove not in groups[group_name]["members"]:
        return "\n[!] Member not found in group."
    groups[group_name]["members"].remove(member_to_remove)
    return f"\n[+] {member_to_remove} removed from group '{group_name}'."

#------------------------------------------------online users status--------------------------------------------
def get_online_users():
    """Return a nicely formatted list of all connected users."""
    if not clients:
        return "\n[!] No users online."
    return "\n🟢 Online Users: " + ", ".join(clients.keys())

#-------------------------------------------------------------main client function----------------------------
def handle_client(client_socket, client_address):
    try:
        client_socket.send("\nEnter your name: ".encode())
        name = client_socket.recv(1024).decode().strip()
        clients[name] = client_socket

        client_socket.send(f"\n{get_online_users()}\n".encode())
        broadcast_message(f"\n[+] {name} has joined the chat!", sender=name)
        broadcast_message(get_online_users())

        print(f"\n[+] {name} connected from {client_address}")

        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            data = data.strip()

            print("\nSERVER GOT THE DATA FROM CLIENT : ", data)

            # --------------- Typing detection ----------------
            if data.startswith("TYPING:"):
                try:
                    target = data[len("TYPING:"):].strip()

                    typing_message = f"\n[{name}] is typing..."

                    if target.lower() == "all":
                        broadcast_message(typing_message, sender=name)
                    elif target in clients:
                        clients[target].send(typing_message.encode())
                    elif target in groups:
                        for member in groups[target]["members"]:
                            if member != name:
                                clients[member].send(typing_message.encode())
                    else:
                        client_socket.send(f"\n[!] Target '{target}' not found.\n".encode())

                except Exception as e:
                    print(f"\n[!] Typing indicator error: {e}")
                continue  # skip rest of loop for typing notification

            # --------------- Group create ---------------
            if data.lower().startswith("creategroup"):
                try:
                    temp = data[len("creategroup"):].strip()
                    if temp.startswith(":"):
                        temp = temp[1:].strip()
                    group_name_part, members_part = temp.split(":", 1)
                    group_name = group_name_part.strip()
                    members = [m.strip() for m in members_part.split(",")]

                    response = create_group(group_name, name, members)
                    client_socket.send((response + "\n").encode())
                except Exception as e:
                    print(f"\n[!] Group creation error: {e}")
                    client_socket.send("\nInvalid group creation format. Use 'creategroup: groupname : user1, user2'\n".encode())
                continue

            # --------------- Group send ---------------
            if data.lower().startswith("sendgroup"):
                try:
                    temp = data[len("sendgroup"):].strip()
                    if temp.startswith(":"):
                        temp = temp[1:].strip()
                    group_name_part, message_part = temp.split(":", 1)
                    group_name = group_name_part.strip()
                    message = message_part.strip()

                    response = send_group_message(group_name, name, message)
                    client_socket.send((response + "\n").encode())
                except Exception as e:
                    print(f"\n[!] Group message error: {e}")
                    client_socket.send("\nInvalid group message format. Use 'sendgroup: groupname : message'\n".encode())
                continue

            # --------------- Group remove member ---------------
            if data.lower().startswith("removefromgroup"):
                try:
                    temp = data[len("removefromgroup"):].strip()
                    if temp.startswith(":"):
                        temp = temp[1:].strip()
                    group_name_part, member_part = temp.split(":", 1)
                    group_name = group_name_part.strip()
                    member_to_remove = member_part.strip()

                    response = remove_member(group_name, name, member_to_remove)
                    client_socket.send((response + "\n").encode())
                except Exception as e:
                    print(f"\n[!] Remove member error: {e}")
                    client_socket.send("\nInvalid remove format. Use 'removefromgroup: groupname : membername'\n".encode())
                continue

            # --------------- Selective broadcast ---------------
            if data.lower().startswith("sendto"):
                try:
                    temp = data[len("sendto"):].strip()
                    if temp.startswith(":"):
                        temp = temp[1:].strip()
                    targets_part, message_part = temp.split(":", 1)
                    targets = [t.strip() for t in targets_part.split(",")]
                    message = message_part.strip()

                    if not message:
                        client_socket.send("\nMessage cannot be empty.\n".encode())
                        continue

                    selective_broadcast(f"{name} (Selective Broadcast): {message}", targets, sender=name)

                except Exception as e:
                    print(f"\n[!] Selective broadcast error: {e}")
                    client_socket.send("\nInvalid format! Use 'sendto: user1, user2 : message'\n".encode())
                continue

            # --------------- Normal private or broadcast ---------------
            if ":" not in data:
                client_socket.send("\nInvalid format! Use 'username: message'\n".encode())
                continue

            receiver_name, message = data.split(":", 1)
            receiver_name = receiver_name.strip()
            message = message.strip()

            if receiver_name.lower() == "all":
                broadcast_message(f"{name} (Broadcast): {message}", sender=name)
            elif receiver_name in clients:
                receiver_socket = clients[receiver_name]
                full_message = f"\n{name} says: {message}"
                receiver_socket.send(full_message.encode())
            else:
                client_socket.send(f"\nUser '{receiver_name}' not found.\n".encode())

    except Exception as e:
        print(f"\n[-] Error with {client_address}: {e}")

    finally:
        print(f"\n[-] {name} disconnected")
        if name in clients:
            del clients[name]
        for n, s in list(clients.items()):
            if s == client_socket:
                del clients[n]
                break

        broadcast_message(f"\n[-] {name} has left the chat.")
        broadcast_message(get_online_users())
        client_socket.close()

# ------------------------------------------------server starter--------------------------------------------------
def start_server(server_ip="127.0.0.1", port=6666, max_clients=10):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((server_ip, port))
    except Exception as e:
        print(f"\n[-] Failed to bind server: {e}")
        return

    server_socket.listen(max_clients)
    print(f"\n[+] Server started on {server_ip}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True).start()

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 6666
    start_server(server_ip=HOST, port=PORT)




