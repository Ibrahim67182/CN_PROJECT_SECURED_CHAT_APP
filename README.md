# 🔐 Secure Chat App with End-to-End Encryption

A real-time, multi-client secure chat system built using Python sockets. Supports one-to-one, group, and broadcast messaging with AES-based end-to-end encryption—ensuring that **even the server cannot read your messages**.

> Developed by: [Ibrahim Junaid (22K-4563)] and [Anas Ahmed (22K-4154)]  
> National University of Computer & Emerging Sciences

---

## 🚀 Features

- ✅ **End-to-End Encryption (AES-128)**  
  All messages are encrypted before leaving the client and decrypted only by the recipient.

- 👤 **Private Messaging**  
  One-to-one secure messaging between clients.

- 📢 **Broadcast & Selective Broadcast**  
  Send messages to all or a selected set of connected clients.

- 👥 **Group Chats**  
  - Create/Delete groups  
  - Add/Remove members  
  - Group-based messaging with sender identification

- ✍️ **Typing Indicators**  
  Real-time typing notifications for individuals and group members.

- ⏱ **Message Editing**  
  Prompt to edit messages with a 20-second timeout before sending.

- 🛡 **Tamper Detection**  
  The server can simulate tampering with a 10% chance—clients will detect and reject modified messages.

- 📶 **Multi-Device Support**  
  Works across multiple devices on the same network via a centralized server.

- 📜 **Online Users Tracking**  
  See who is currently online.

- 📬 **Delivery Acknowledgements**  
  Clients are informed whether their message was successfully delivered or blocked.

---

## 🧩 System Architecture

[Client A] <---> <---> [Client B]
\ /
\ /
[ Central Python Server ]


- Clients encrypt messages before sending
- Server simply forwards encrypted data
- Recipients decrypt messages locally

---



## 💻 Tech Stack

| Category     | Tools / Tech                              |
|--------------|--------------------------------------------|
| Language     | Python 3.12.1                              |
| Networking   |  socket ,  threading                       |
| Encryption   | Custom AES (from [ boppreh/aes ](https://github.com/boppreh/aes)) |
| IDE          | Visual Studio Code                         |
| Platform     | Windows                                    |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
bash
git clone https://github.com/your-username/secure-chat-app.git
cd secure-chat-app


### 2. Run the Server
Update HOST in server.py to your local IP address (e.g., 192.168.x.x) and start the server:

## python server.py

### 3. Run the Client(s)
On the same or different devices (connected to same network):  (for different devices use cnetral server ip of one of device and make sure each device is connected to same wifi)

## python client.py


## 🧪 Usage
Once connected, follow the command formats:

| Command           | Example                               |
| ----------------- | ------------------------------------- |

| Private Message   |  ali : Hello                          |

| Broadcast to All  |  all : Hello everyone                 |

| Selective Message |  sendto: user1, user2 : Hello         |

| Create Group      |  creategroup: mygroup : user1,user2   |

| Group Message     |  sendgroup: mygroup : Hello everyone  |

| Remove from Group |  removefromgroup: mygroup: user1      |

| Exit Chat         |  exit                                 |


## 🗂 Project Modules
server.py: Multi-threaded Python socket server

client.py: Interactive command-line client with encryption

aes_encryption.py: AES encryption/decryption utilities



## 📚 References
Python Sockets: https://docs.python.org/3/howto/sockets.html

AES Algorithm: https://github.com/boppreh/aes

Networking Concepts: Kurose & Ross, Tanenbaum

Threading Help: https://stackoverflow.com/questions/72565884


## 📄 License
This project is for academic and educational purposes.


## 🔗 Connect
✉️ Ibrahim Junaid -  https://github.com/Ibrahim67182


✉️ Anas Ahmed -      https://github.com/anasahmed81103




