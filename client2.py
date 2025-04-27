import socket
import threading
import time

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"\n{message}\nYou: ", end='')  # Keep cursor ready for next input
        except:
            print("\n[!] Connection closed by server.")
            break


# ------------------------------------------------------typin status indicator function-------------------------------


def send_typing_notification(client_socket, target):
    try:
        typing_signal = f"TYPING:{target}"
        client_socket.send(typing_signal.encode())
   
    except:
        print("Typing indicator error occured")





def main():
    server_ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    server_port = 6666

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return

    # Receive server's name prompt
    try:
        name_prompt = client_socket.recv(1024).decode()
        print(name_prompt, end='')
        name = input()
        client_socket.send(name.encode())
        print(f"[+] Connected as '{name}'!")
    except Exception as e:
        print(f"[-] Failed during name setup: {e}")
        return

    # Start a background thread for receiving messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    while True:
            print("\n=== Messaging Formats ===")
            print("To send a private message:         username : your_message")
            print("To broadcast to all users:         all : your_message")
            print("To send to multiple users:         sendto: user1, user2 : your_message")
            print("To Create Group:                   creategroup: my_group : user1,user2")
            print("To send message in Group:          sendgroup : mygroup : Hello Mmebers")
            print("To remove user from Group:         removefromgroup: mygroup: user3")
            print("To exit the chat:                  type 'exit'")
            print("==========================\n")

        
            msg = input("You: ")

            if msg.lower() == "exit":
                break

            try:
                if ":" in msg:
                    receiver_part = msg.split(":", 1)[0].strip()
                    send_typing_notification(client_socket, receiver_part)
               
                    time.sleep(0.5)  # small delay for realism
                
                # after delay send the actual message after typing indicator 
                
            
                client_socket.send(msg.encode())
            
            
            except Exception as e:
               
                print(f"[-] Failed to send message: {e}")
                break




    client_socket.close()
    print("[+] Disconnected from server.")

if __name__ == "__main__":
    main()
