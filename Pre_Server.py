# This file is used for sending the file over socket
import os
import socket
import time

# Creating a socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), 9999))
sock.listen(1)

# Waiting for connection.
print("Server is listening for connections...")

# Accepting the connection.
client, addr = sock.accept()
print(f"Connection established with {addr}")

# Receive action from client
action = client.recv(100).decode().strip()

if action == "upload":
    # Receive a file from the client
    file_name = client.recv(100).decode().strip()
    file_size = int(client.recv(100).decode().strip())

    SAVE_DIR = r"C:\\Tuyen\\Socket\\Test Server dir"
    save_path = os.path.join(SAVE_DIR, file_name)
    with open(save_path, "wb") as file:
        received_size = 0
        while received_size < int(file_size):
            data = client.recv(1024)
            if not data:
                break
            file.write(data)
            received_size += len(data)

    print(f"File '{file_name}' received and saved.")

elif action == "download":
    # Getting file name from server.
    file_name = input("File Name:").strip()
    if not os.path.exists(file_name):
        print(f"File '{file_name}' not found!")
        client.close()
        exit(0)

    # Get file size.
    file_size = os.path.getsize(file_name)

    # Sending file_name and size.
    client.send(file_name.encode())
    client.send(str(file_size).encode())

    # Opening file and sending data.
    with open(file_name, "rb") as file:
        # Starting the time capture.
        start_time = time.time()

        while chunk := file.read(1024):
            client.send(chunk)

        # Ending the time capture.
        end_time = time.time()

    print("File Transfer Complete.Total time: ", end_time - start_time)

else:
    print("Invalid action received.")
    client.close()

# Cloasing the socket.
sock.close()