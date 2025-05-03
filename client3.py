
import socket
import threading
import time
from aes_encryption import aes_encrypt_block, aes_decrypt_block, generate_key


instructions = (
    "\n=== Messaging Formats ===\n"
    "🔷  To send a private message:         username : your_message\n"
    "🔷  To broadcast to all users:         all : your_message\n"
    "🔷  To send to multiple users:         sendto: user1, user2 : your_message\n"
    "🔷  To Create Group:                   creategroup: my_group : user1,user2\n"
    "🔷  To send message in Group:          sendgroup : mygroup : Hello Members\n"
    "🔷  To remove user from Group:         removefromgroup: mygroup: user3\n"
    "🔶  To exit the chat:                  type 'exit'\n"
    "==========================\n"
)






def receive_messages(client_socket , key):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break

            message = data.decode().strip()

    
            # --- Group Message ---
            if message.startswith("[Group:"):
                try:
                    group_end = message.index("]")
                    group_name = message[7:group_end]
                    rest = message[group_end+1:].strip()
                    sender, ciphertext = rest.split(":", 1)
                    sender = sender.strip()
                    ciphertext = ciphertext.strip()

                    # Check if ciphertext is hex
                    if all(c in '0123456789abcdefABCDEF' for c in ciphertext.replace(" ", "")):
                        plaintext = aes_decrypt_block(ciphertext, key)
                        print(f"\n[Group:{group_name}] {sender}: {plaintext}")
                        continue
                except Exception as e:
                    print(f"\n[!] Failed to decrypt group message: {e}")
                    print(f"\n[Raw] {message}")
                    continue

            # --- Private or Broadcast Message ---
            if ':' in message:
                try:
                    sender, ciphertext = message.split(":", 1)
                    sender = sender.strip()
                    ciphertext = ciphertext.strip()

                    if all(c in '0123456789abcdefABCDEF' for c in ciphertext.replace(" ", "")):
                        plaintext = aes_decrypt_block(ciphertext, key)
                        print(f"\n{sender} : {plaintext}")
                        continue
                except Exception as e:
                    print(f"\n[!] Error decrypting message: {e}")
                    print(f"\n[Raw Message] {message}")
                    continue

            # --- Fallback (non-encrypted or system messages) ---
            print(f"\n{message}")

        except Exception as e:
            print(f"\n [!] Error receiving message: {e}")
            break




def send_typing_notification(client_socket, target):
    try:
        typing_signal = f"TYPING:{target}"
        client_socket.send(typing_signal.encode())
    except:
        print("\n Typing indicator error occurred")






def format_and_encrypt_message(msg: str , key) -> str:
    msg = msg.strip()

    if msg.startswith("creategroup:") or msg.startswith("removefromgroup:"):
        return msg  # send as-is

    if msg.startswith("sendto:"):
        parts = msg.split(":", 2)
        if len(parts) == 3:
            command, users, content = parts
            encrypted = aes_encrypt_block(content.strip(), key)
            return f"{command.strip()}: {users.strip()} : {encrypted}"

    elif msg.startswith("sendgroup:"):
        parts = msg.split(":", 2)
        if len(parts) == 3:
            command, group, content = parts
            encrypted = aes_encrypt_block(content.strip(), key)
            return f"sendgroup:{group.strip()}:{encrypted}"


    elif msg.startswith("all"):
        parts = msg.split(":", 1)
        if len(parts) == 2:
            command, content = parts
            encrypted = aes_encrypt_block(content.strip(), key)
            return f"{command.strip()} : {encrypted}"

    elif ":" in msg:
        parts = msg.split(":", 1)
        if len(parts) == 2:
            username, content = parts
            encrypted = aes_encrypt_block(content.strip(), key)
            return f"{username.strip()} : {encrypted}"

    return msg  # fallback, send raw if format not matched



def main():

    key = generate_key()

    server_ip = input("\nEnter server IP (default 127.0.0.1): ") or "127.0.0.1"
    server_port = 6666

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
    except Exception as e:
        print(f"\n [-] Connection failed: {e}")
        return

    try:
        name_prompt = client_socket.recv(1024).decode()
        print(name_prompt, end='')
        name = input()
        client_socket.send(name.encode())
        print(f"\n [+] Connected as '{name}'!")
    except Exception as e:
        print(f"\n [-] Failed during name setup: {e}")
        return

    threading.Thread(target=receive_messages, args=(client_socket,key), daemon=True).start()

    while True:
       
        print("\n"+instructions)

        msg = input("\nYou:  ")

     
        

        if msg.lower() == "exit":
            break

        if ":" in msg:
            lower_msg = msg.lower()
            target = None

            if lower_msg.startswith("sendgroup:"):
                try:
                    _, group, _ = msg.split(":", 2)
                    target = group.strip()
                except:
                    pass

            elif lower_msg.startswith("sendto:"):
                try:
                    _, users, _ = msg.split(":", 2)
                    target = users.strip()
                except:
                    pass

            elif lower_msg.startswith("all"):
                target = "all"

            else:
                try:
                    target = msg.split(":", 1)[0].strip()
                except:
                    pass

            if target:
                send_typing_notification(client_socket, target)
                time.sleep(0.3)
        
            


        try:
            final_message = format_and_encrypt_message(msg,key)
            client_socket.send(final_message.encode())

        except Exception as e:
            print(f"\n [-] Failed to send message: {e} Retry!")
            break

    client_socket.close()
    print("\n[+] Disconnected from server.")

if __name__ == "__main__":
    main()
