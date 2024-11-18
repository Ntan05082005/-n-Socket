# This file will be used for recieving files over socket connection.
import os
import socket
import time


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Trying to connect to socket.
try:
    sock.connect((socket.gethostname(), 9999))
    print("Connected Successfully")
except:
    print("Unable to connect")
    exit(0)

# Action: Uploading/ Downloading
action = input("Enter 'upload' to send a file or 'download' to receive a file: ").strip().lower()
sock.send(action.encode());

if action == "upload":
    file_name = input("Enter the file name to upload: ").strip()

    if not os.path.exists(file_name):
        print(f"File '{file_name}' not found!")
        sock.close()
        exit(0)

    file_size = os.path.getsize(file_name)
    sock.send(file_name.encode())
    sock.send(str(file_size).encode())

    with open(file_name, "rb") as file:
        while chunk := file.read(1024):
            sock.send(chunk)

    print(f"File '{file_name}' uploaded successfully.")


elif action == "download":
    # Send file details.
    file_name = sock.recv(100).decode()
    file_size = sock.recv(100).decode()

    # Opening and reading file.
    with open("C:/Tuyen/Socket/Test Client Dir/" + file_name.strip(), "wb") as file:
        recieved_size = 0
        # Starting the time capture.
        start_time = time.time()

        # Running the loop while file is recieved.
        while recieved_size <= int(file_size):
            data = sock.recv(1024)
            if not (data):
                break
            file.write(data)
            recieved_size += len(data)

        # Ending the time capture.
        end_time = time.time()

    print("File transfer Complete.Total time: ", end_time - start_time)

else:
    print("Invalid action.")
    sock.close()
    exit(0)

# Closing the socket.
sock.close()