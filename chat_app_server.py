import socket
import threading
import random
import string


clients = {}  #    {client_name: client_socket}    # for maintaing clients with proper sockets attached to names for proper communication 
groups = {}  #     {creator: creator_name ,  members : [member1, member2 , ......]}     # group management who created the group and members added in it


# ----------------------------------------------------broadcasting message to all clients -----------------------------------------

 # Send a message to all clients connected to the server except sender sending the message 

def broadcast_message(message, sender=None):
    
    for name, client_socket in clients.items():
       
        if name != sender:
            try:
                client_socket.send(message.encode())
           
            except:
                print("\n[!] Error broadcasting the message to", name)



# ----------------------------------------------------selective broadcasting------------------------------

#  Send a message to selected clients only among the list of already connected clients 

def selective_broadcast(message, target_clients_list, sender=None):
    
    for target_name in target_clients_list:
       
        if target_name in clients and target_name != sender:
       
            try:
                clients[target_name].send(message.encode())
       
            except:
                print(f"\n[!] Error sending selective broadcast to {target_name}")



# ------------------------------------------------group messages and group management functions -------------------------------------


#  Send messages  to all members of a group  is group not exist and member name not valid exception occurs 

def send_group_message(group_name, sender, message):
    
    
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
    
    return "\nMessage successfully sent to group."


#   Create a new group with validation and notify members that a they are added by the client with name 

def create_group(group_name, creator, members):
   
    if group_name in groups:
        return "\n[!] Group already exists."

    
    for member in members:
        
        if member not in clients:
            return f"\n[!] User '{member}' not found. Please add only connected users."

   
    all_members = list(set(members + [creator]))
   
    groups[group_name] = {"creator": creator, "members": all_members}

   
    # Notify each member (excluding creator) about group creation
    for member in all_members:
       
        if member != creator:
            try:
                clients[member].send(f"\n[*] You have been added to the group '{group_name}' by {creator}.".encode())
            except:
                print("\nError Adding the member to the group")

  
    return f"\n[+] Group '{group_name}' created successfully with members: {', '.join(all_members)}"


#   Remove a member from a group which can only be done by creator  and notify them (normal member cannot remove any one from group)


def remove_member(group_name, remover, member_to_remove):
   
    
    if group_name not in groups:
    
        return "\n[!] Group not found."
    
    if groups[group_name]["creator"] != remover:
    
        return "\n[!] Only group creator can remove members."
    
    if member_to_remove not in groups[group_name]["members"]:
    
        return "\n[!] Member not found in group."

    groups[group_name]["members"].remove(member_to_remove)

    
    # Notify removed member
    
    if member_to_remove in clients:
    
        try:
            clients[member_to_remove].send(f"\n[*] You have been removed from the group '{group_name}' by {remover}.".encode())
        except:
           print("\nError removing member from the group")

    return f"\n[+] {member_to_remove} removed from group '{group_name}'."



#------------------------------------------------online users status--------------------------------------------

 #  Return a nicely formatted list of all connected users currently connected with the server so you can see them 

def get_online_users():
   
    if not clients:
    
        return "\n[!] No users online."
    
    return "\n🟢 Online Users: " + ", ".join(clients.keys())



#---------------------------------------------------message modification by server -----------------------------------------

# this function is for security check that if server try to change the message then this message will be detected and not send to reciver 


def message_tampering(org_message):

   if random.random() <0.10:   # chance of message  tampering  by server is 10% probabilty  
    
        length = random.randint(10,20)
       
        new_msg = org_message + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)) 
       
        return new_msg , True
   
   return org_message , False    # returning orginal message or tampered message with status 



#--------------------------------------------------edit message feature for clients ----------------------------------------
 
# this function give 20 sec time to edit message if accidentally typed and then send it if no response automatically send after 20 sec  

def edit_messages(client_socket, original_message, sender, prompt_type):
    
    
    client_socket.send(
        f"\n🕒 Do you want to edit this {prompt_type} message or send it now?"
        
        f" (Type 'edit' to modify or 'send' to continue)\n"
        
        f"⏳ Auto-sending in 20 seconds...\n".encode()
    )


    client_socket.settimeout(20.0)         
    
    try:
        response = client_socket.recv(1024).decode().strip().lower()
        
        if response == "edit":
           
            client_socket.send("\n✏️ Enter the edited message: ".encode())
            new_message = client_socket.recv(1024).decode().strip()
            return new_message
        
        elif response == "send":
            return original_message
    
    except socket.timeout:
        client_socket.send("\n⏰ Time's up! Sending the message as is...\n".encode())
    
    finally:
        client_socket.settimeout(None)

    return original_message




#-------------------------------------------------------------main client function-------------------------------------

# for managing each client messages and send to appropriate clients sockets for proper and smooth messaging communication 


def handle_client(client_socket, client_address):
   
    try:
      
        client_socket.send("\nEnter your name: ".encode())
      
        name = client_socket.recv(1024).decode().strip()
      
        clients[name] = client_socket                            # connecting client with name and storing proper socket for names

       
        broadcast_message(f"\n[+] {name} has joined the chat!", sender=name)
       
        broadcast_message(get_online_users())                    # display updated online users 

        print(f"\n[+] {name} connected from {client_address}")

       
        while True:
            
            data = client_socket.recv(1024).decode()
            
            if not data:
                break

            data = data.strip()

            print("\nSERVER GOT THE DATA FROM CLIENT : ", data)           # encrypted data reciving from sender client to send to appropriate client 
                                                                           # server cannot see the actual message 
            # --------------- Typing detection ----------------
          
            if data.startswith("TYPING:"):                              # handling typing notifications 
             
                try:
                    target = data[len("TYPING:"):].strip()
                    typing_message = f"\n[{name}] is typing..."

                    if target.lower() == "all":
                        broadcast_message(typing_message, sender=name)

                    elif target in groups:
                    
                        # Send to all group members except the sender
                        for member in groups[target]["members"]:
                            if member != name and member in clients:
                                clients[member].send(typing_message.encode())

                    else:
                       
                        # handling multiple typing notification to users 
                       
                        targets = [t.strip() for t in target.split(",")]
                        for t in targets:
                           
                            if t in clients and t != name:
                                clients[t].send(typing_message.encode())
                           
                            elif t not in clients and t not in groups:
                                client_socket.send(f"\n[!] Target '{t}' not found.\n".encode())

                except Exception as e:
                    print(f"\n[!] Typing indicator error: {e}")
             
                continue  # skip rest of loop for typing notification



            # --------------- Group create ---------------
           
            if data.lower().startswith("creategroup"):                                # extracting message to check if client requests to create group 
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


            # --------------- Group send ---------------                    # sending group message with edit handle and also check for tampering 
            if data.lower().startswith("sendgroup"):
                try:
                   
                    temp = data[len("sendgroup"):].strip()
                   
                    if temp.startswith(":"):
                   
                        temp = temp[1:].strip()
                   
                    group_name_part, message_part = temp.split(":", 1)
                   
                    group_name = group_name_part.strip()
                    
                    message = edit_messages(client_socket, message_part.strip(), name, f"group '{group_name}'")


                    final_message, tampered = message_tampering(message)

                   
                    if tampered:
                         client_socket.send("\n[!] ⚠️   Group Message was tampered  by server!\n ❌  Message Not sent..   \n".encode())
                         continue
                    
                    else:
                         response = send_group_message(group_name, name, final_message)
                         client_socket.send((response + "\n").encode())
                         client_socket.send(f" ✅  Message delivered to {group_name}.\n".encode())
         

                except Exception as e:
                    print(f"\n[!] Group message error: {e}")
                    client_socket.send("\nInvalid group message format. Use 'sendgroup: groupname : message'\n".encode())
                continue


            # --------------- Group remove member ---------------
            if data.lower().startswith("removefromgroup"):                        # to remove memeber from the group and also check that creator of group initited it
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
            if data.lower().startswith("sendto"):                            # selected clients message delivery with edit option and tamper checking
                try:
                    temp = data[len("sendto"):].strip()
                   
                    if temp.startswith(":"):
                        temp = temp[1:].strip()
                    targets_part, message_part = temp.split(":", 1)
                    targets = [t.strip() for t in targets_part.split(",")]
                   
                    message = edit_messages(client_socket, message_part.strip(), name, "selective")


                    if not message:
                        client_socket.send("\nMessage cannot be empty.\n".encode())
                        continue

                    final_message, tampered = message_tampering(f"{name} (Selective Broadcast): {message}")

                    

                    if tampered:
                        client_socket.send("\n ⚠️   [!] Your selective BCAST message was tampered by the server before broadcasting!\n ❌  Message Not sent..   \n".encode())
                        continue

                    else:
                        selective_broadcast(final_message, targets, sender=name)
                        client_socket.send(f" ✅   Message delivered to {targets}.\n".encode())



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

            if receiver_name.lower() == "all":                     # message for all clients 


                message = edit_messages(client_socket, message, name, "broadcast")
                final_message, tampered = message_tampering(f"{name} (Broadcast): {message}")
                    
                if tampered:
                    client_socket.send("\n ⚠️   [!] Your message was tampered by the server before broadcasting!\n ❌  Message Not sent..   \n".encode())
                    continue
                else:
                    broadcast_message(final_message, sender=name)
                    client_socket.send(f" ✅   Message delivered to {receiver_name}.\n".encode())



           
            elif receiver_name in clients:                             # private message for one-one communication b/w clients 
                
                message = edit_messages(client_socket, message, name, "private")
              
                final_message, tampered = message_tampering(f"\n{name} says: {message}")
               
               
                if tampered:
                    client_socket.send("\n ⚠️   [!] Your private message was tampered by the server before delivery!\n ❌  Message Not sent.. \n".encode())
                    continue

                try:
                     clients[receiver_name].send(final_message.encode())
                     client_socket.send(f"✅   Message delivered to {receiver_name}.\n".encode())
                except:
                     client_socket.send(f"[!] Could not deliver message to {receiver_name}.\n".encode())     


            else:
                client_socket.send(f"\nUser '{receiver_name}' not found.\n".encode())


    except Exception as e:
        print(f"\n[-] Error with {client_address}: {e}")

    finally:
      
        print(f"\n[-] {name} disconnected")                              # disconnect clients handling 
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

# intializing server and to with proper ip and port to connect clients using sockets 

def start_server(server_ip="127.0.0.1", port=7777, max_clients=10):
   
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
    
    HOST = "192.168.100.40"    # my local ip address  ( ypu can made cebtral server your pc and use your local ip address)
    
    PORT = 3009          # can allocate any free port 
    
    start_server(server_ip=HOST, port=PORT)




