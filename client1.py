
import socket
import threading
import time


# module used from our local files for encryption using aes methods 
from aes_encryption import aes_encryption, aes_decryption, generate_key

# instruction prompt display at top for guide to use app 

chat_app_instructions = (
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


#-----------------------------------------------------------------for Receiving messages------------------------------------

# main function for receiving messages and properly extract content from format and decrypt it 


def receive_messages(client_socket , key):
   
   
    while True:
      
        try:
           
            data = client_socket.recv(4096)
            
            if not data:
                break

            message = data.decode().strip()
    
            # --- for Group Message ---
            if message.startswith("[Group:"):
                try:
                  
                    group_end = message.index("]")
                  
                    group_name = message[7:group_end]
                  
                    remaining_content = message[group_end+1:].strip()
                  
                    sender, ciphertext = remaining_content.split(":", 1)
                  
                    sender = sender.strip()
                  
                    encrypted_text = ciphertext.strip()

                    # Check if ciphertext is hex
                  
                    if all(c in '0123456789abcdefABCDEF' for c in encrypted_text.replace(" ", "")):
                  
                        decrypted_text = aes_decrypt_block(encrypted_text, key)
                  
                        print(f"\n[Group:{group_name}] {sender}: {decrypted_text}")
                        continue
                
                except Exception as e:
                
                    print(f"\n[!] Failed to decrypt group message: {e}")
                    print(f"\n[Raw] {message}")
                    continue

            # --- for Private or Broadcast Messages ---
            
            if ':' in message:
                try:
                    
                    sender, ciphertext = message.split(":", 1)
                    
                    sender = sender.strip()
                    
                    encrypted_text = ciphertext.strip()

                   
                    if all(c in '0123456789abcdefABCDEF' for c in encrypted_text.replace(" ", "")):
                   
                        decrypted_text = aes_decrypt_block(encrypted_text, key)
                   
                        print(f"\n{sender} : {decrypted_text}")
                   
                        continue
                
                except Exception as e:
                    print(f"\n[!] Error decrypting message: {e}")
                    print(f"\n[Raw Message] {message}")
                    continue

           
            # --- non-encrypted or any  system message   ---
            print(f"\n{message}")


        except Exception as e:
            print(f"\n [!] Error receiving message: {e}")
            break



#----------------------------------------------------typing indicator function------------------------------------

# send typing notification to proper clients concerned 

def send_typing_notification(client_socket, target):  
  
    try:
  
        typing_signal = f"TYPING:{target}"
  
        client_socket.send(typing_signal.encode())
  
    except:
  
        print("\n Typing indicator error occurred")




#-----------------------------------------------------------message extractor and encrypt content--------------------------------------

# this fucntion is to extract actual message from raw message format and encrypt it and agian properly format it but with encryption

# e.g     all : broadcast message 


def format_and_encrypt_message(msg , key):
    
    msg = msg.strip()

    if msg.startswith("creategroup:") or msg.startswith("removefromgroup:"):
        
        return msg  


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


    return msg  #  send raw if format not matched



#----------------------------------------------------------main function----------------------------------------

# to handle all message sending and reciving operations using clean and proper main function

def main():

    key = generate_key()

   
    server_ip = input("\nEnter server IP (default 127.0.0.1): ") or "127.0.0.1"
   
    server_port =  3009  # allocate proper server port 

    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((server_ip, server_port))
    
    except Exception as e:
        print(f"\n [-] Failure Connecting to the Server : {e}")
        return

    try:
       
        name_prompt = client_socket.recv(1024).decode()
       
        print(name_prompt, end='')
        
        name = input()           # taking name input to identify you with name 
        client_socket.send(name.encode())
        
        print(f"\n [+] Connected to SERVER as : '{name}'!")
    

    except Exception as e:
        print(f"\n [-] Failed during name setup : {e}")
        return


    threading.Thread(target=receive_messages, args=(client_socket,key), daemon=True).start()

    while True:
       
        print("\n"+chat_app_instructions)

        msg = input("\nYou:  ")

        if msg.lower() == "exit":                  # for exit the chat 
            break

        if ":" in msg:
            
            lower_msg = msg.lower()
            
            target = None

            if lower_msg.startswith("sendgroup:"):          # handle group messages to send to proper group
                try:
                    _, group, _ = msg.split(":", 2)
                    target = group.strip()
                except:
                    pass

            elif lower_msg.startswith("sendto:"):          # handle selective broadcast to send message only to selected users 
                try:
                    _, users, _ = msg.split(":", 2)
                    target = users.strip()
                except:
                    pass


            elif lower_msg.startswith("all"):               # for broadasting message to all users 
                target = "all"

            else:
                try:
                    target = msg.split(":", 1)[0].strip()          # for hnadling private message for proper username
                except:
                    pass

            if target:                                                 
                
                send_typing_notification(client_socket, target)           # sending typing indicator notification 
                
                time.sleep(0.3)
        
            
        try:
            final_encrypted_message = format_and_encrypt_message(msg,key)    # sending proper message after encypting it properly to server
           
            client_socket.send(final_encrypted_message.encode())

        except Exception as e:
           
            print(f"\n [-] Failed to send message: {e} Retry!")
           
            break

 
    client_socket.close()
    print("\n[+] Disconnected from server.")



# to run the code properly in environment and not to run other clients methods 

if __name__ == "__main__":
    main()
