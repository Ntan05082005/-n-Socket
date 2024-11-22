# This file will be used for recieving files over socket connection.
from importlib import simple
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import os
import socket
import time

# Connecting process
def connect_to_server():
    try:
        sock.connect((socket.gethostname(), 9999))
        messagebox.showinfo("Connection", "Connected Successfully")

        switch_to_action_frame()

    except:
        messagebox.showerror("Connection", "Unable to connect")
        exit(0)

# Uploading process
def upload_file():
    # Tkinter's file dialog
    file_name = filedialog.askopenfilename(title = "Select a file to upload").strip()
    file_size = str(os.path.getsize(file_name))
    if not file_name:
        return # not file_name -> no file is selected

    
    sock.send(b"upload") # Notify the upload action
    sock.send(file_name.encode())
    time.sleep(0.01)
    sock.send(file_size.encode())
    
    with open(file_name, "rb") as file:
        while chunk := file.read(1024):
            if not chunk:
                break
            sock.send(chunk)
            
    messagebox.showinfo("Upload", f"File '{file_name}' uploaded successfully")

# Downloading process
def download_file():
    # Tkinter's simple dialog
    file_name = simpledialog.askstring("Download", "Enter the file name to download:")
    if not file_name:
        return # not file_name -> no file is selected

    sock.send(b"download")
    sock.send(file_name.encode())
    # Tkinter's file dialog -> choose dir to save
    save_path = filedialog.asksaveasfile(title="Save download file as", initialfile=file_name)
    if not save_path:
        return # not save_path -> no path is chosen

    with open(save_path, "wb") as file:
        while chunk := sock.recv(1024):
            if not chunk:
                break # not chunk -> no more data is received
            file.write(chunk)

    messagebox.showinfo("Download", "File downloaded successfully.")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setup main using Tkinter UI
root = tk.Tk() # tk.Tk: root object for GUI -> create main Tkinter window
root.title("File transfer program")

# Set window size
windowX = 600
windowY = 400
window_size_msg = str(windowX) + "x" + str(windowY)

# Tkinter's geometry() -> set window's initial size
root.geometry(window_size_msg)

# Initial screen frame (frame#1)
connect_frame = tk.Frame(root)
connect_frame.pack(fill="both", expand=True)

# Upload/download options frame (frame#2)
action_frame = tk.Frame(root)

# Function to switch connect frame -> action frame
def switch_to_action_frame():
    connect_frame.pack_forget()
    action_frame.pack(fill="both", expand=True)

# Set button size
btn_width = 150
btn_height = 50
btnX = windowX / 2 - btn_width / 2

# Tkinter's layout
# Connect frame
connect_btn = tk.Button(connect_frame, text="Connect to Server", command=connect_to_server)
connect_btn.place(x=btnX, y=150, width=btn_width, height=btn_height)

exit_btn = tk.Button(connect_frame, text="Exit", command=root.quit) # Tkinter's root.quit
exit_btn.place(x=btnX, y=200, width=btn_width, height=btn_height)

# Action frame
upload_btn = tk.Button(action_frame, text="Upload File", command=upload_file)
upload_btn.place(x=btnX, y=125, width=btn_width, height=btn_height)

download_btn = tk.Button(action_frame, text="Download File", command=download_file)
download_btn.place(x=btnX, y=175, width=btn_width, height=btn_height)

exit_btn = tk.Button(action_frame, text="Exit", command=root.quit) # Tkinter's root.quit
exit_btn.place(x=btnX, y=225, width=btn_width, height=btn_height)

# Tkinter's main event loop
root.mainloop()