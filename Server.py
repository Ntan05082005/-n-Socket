import os
import socket
import time
import threading


# Ensure the filename is unique by appending a counter
def get_unique_filename(directory, filename):
    root, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Check if file exists, if so, append a counter
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{root} ({counter}){ext}"
        counter += 1

    return new_filename


# Main function to create and manage the server
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), 9999))
    sock.listen(5)

    print("Server is listening for connections...")
    try:
        while True:
            client, addr = sock.accept()
            print(f"New connection from {addr}")

            # Start a new thread for each client
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()

            # Show active thread count
            print(f"[Active connections] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("[SERVER] Server shutting down...")
    finally:
        sock.close()


# Handle individual client
def handle_client(client, addr):
    print(f"Connection established with {addr}")
    connected = True

    while connected:
        try:
            action = client.recv(100).decode().strip().lower()
            print(f"Received action from {addr}: '{action}'")

            if not action:
                print("No action received. Closing connection.")
                break

            if action == "!disconnect":
                connected = False
                print(f"Disconnected from {addr}")

            elif action == "upload":
                handle_upload(client)

            elif action == "download":
                handle_download(client)

            else:
                print("Invalid action received.")
                client.send(b"Invalid action")

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    client.close()
    print(f"Connection with {addr} closed.")


# Handle file uploads
def handle_upload(client):
    try:
        file_name = client.recv(100).decode().strip()
        file_size = int(client.recv(100).decode().strip())

        # Change SAVE_DIR when used
        SAVE_DIR = r"C:\Tuyen\Socket\Test Server dir"
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        # Ensure a unique file name
        unique_file_name = get_unique_filename(SAVE_DIR, os.path.basename(file_name))
        save_path = os.path.join(SAVE_DIR, unique_file_name)

        with open(save_path, "wb") as file:
            received_size = 0
            while received_size < file_size:
                data = client.recv(1024)
                if not data:
                    break
                file.write(data)
                received_size += len(data)

        print(f"File '{unique_file_name}' received and saved successfully.")
        client.send(b"Upload complete")
    except Exception as e:
        print(f"Error during upload: {e}")
        client.send(b"Upload failed")


# Handle file downloads
def handle_download(client):
    try:
        file_name = client.recv(100).decode().strip()

        if not os.path.exists(file_name):
            print(f"File '{file_name}' not found!")
            client.send(b"File not found")
            return

        file_size = os.path.getsize(file_name)
        client.send(file_name.encode())
        client.send(str(file_size).encode())

        with open(file_name, "rb") as file:
            start_time = time.time()
            while chunk := file.read(1024):
                client.send(chunk)
            end_time = time.time()

        print(f"File '{file_name}' sent successfully. Total time: {end_time - start_time:.2f} seconds.")
        client.send(b"Download complete")
    except Exception as e:
        print(f"Error during download: {e}")
        client.send(b"Download failed")


if __name__ == "__main__":
    main()
