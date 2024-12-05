import os
import socket
import json
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
    sock.settimeout(1)

    print("Server is listening for connections...\n")
    try:
        while True:
            try:
                client, addr = sock.accept()
                print(f"New connection from {addr}")

                # Start a new thread for each client
                thread = threading.Thread(target=handle_client, args=(client, addr))
                thread.start()

                # Show active thread count
                print(f"[Active connections] {threading.active_count() - 1}\n")

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("[SERVER] Server shutting down...\n")

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

            if action == "disconnect":
                connected = False
                print(f"Disconnected from {addr}")

            elif action == "upload":
                handle_upload(client)

            elif action == "download":
                handle_download(client)

            elif action == "upload_folder":
                handle_folder_upload(client)

            else:
                print("Invalid action received.")
                client.send(b"Invalid action")

            print("\n")

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    client.close()
    print(f"\nConnection with {addr} closed.\n")


# Handle file uploads
def handle_upload(client):
    try:
        metadata = client.recv(1024).decode().strip()
        metadata = json.loads(metadata)  # Convert JSON string to dictionary

        file_name = metadata["file_name"]
        file_size = int(metadata["file_size"])

        if not file_name or not file_size:
            raise Exception("Upload", "Metadata not received")
        else:
            client.send(b"ACK")

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

        client.send(b"ACK")

    except Exception as e:
        client.send(b"NACK")
        print(f"Error during upload: {e}")

def handle_folder_upload(client):
    try:
        # Receive metadata
        metadata = client.recv(1024).decode().strip()
        metadata = json.loads(metadata)  # Convert JSON string to dictionary

        # Extract metadata
        folder_path = metadata["folder_path"]
        num_files = int(metadata["num_files"])

        # ACK handling for metadata
        if not folder_path or not num_files:
            raise Exception("Folder upload", "Metadata not received")
        else:
            client.send(b"ACK")

        # Create dir
        SAVE_DIR = r"C:\Tuyen\Socket\Test Server dir"
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        # Create a new folder to store the files
        folder_name = os.path.basename(folder_path)
        folder_save_path = os.path.join(SAVE_DIR, folder_name)
        if not os.path.exists(folder_save_path):
            os.makedirs(folder_save_path)

        print(f"Receiving folder: {folder_path} with {num_files} files...")

        # Receive all files in the folder
        for _ in range(num_files):
            # Receive file metadata
            metadata = client.recv(1024).decode().strip()
            metadata = json.loads(metadata)  # Convert JSON string to dictionary

            # Extract metadata
            file_name = metadata["file_name"]
            file_size = int(metadata["file_size"])

            # ACK handling for file metadata
            if not file_name or not file_size:
                raise Exception("Folder upload", "File metadata not received")
            else:
                client.send(b"ACK")

            # Ensure a unique file name
            unique_file_name = get_unique_filename(folder_save_path, os.path.basename(file_name))
            save_path = os.path.join(folder_save_path, unique_file_name)

            # Receive and save 1 file
            with open(save_path, "wb") as file:
                received_size = 0
                while received_size < file_size:
                    data = client.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    received_size += len(data)

            print(f"File '{unique_file_name}' received and saved successfully.")

            # ACK handling for file uploading completion
            client.send(b"ACK")

        # ACK handling for folder uploading completion
        client.send(b"ACK")
    except Exception as e:
        client.send(b"NACK")
        print(f"Error during folder upload: {e}")


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