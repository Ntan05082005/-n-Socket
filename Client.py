# This file will be used for recieving files over socket connection.
from importlib import simple
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from tkinter import ttk
import os
import socket
import json
import time

socket_is_connected = False

# Global variables for progress screen
progress_screen, progress_bar, progress_label = None, None, None

# Connecting process
def connect_to_server():

    global socket_is_connected

    try:
        if not ip_default_var.get():
            ip = ip_var.get()
        else:
            ip = socket.gethostname()

        if not port_default_var.get():
            port = int(port_var.get())
        else:
            port = 9999

        sock.connect((ip, port))
        messagebox.showinfo("Connection", "Connected Successfully")
        socket_is_connected = True
        switch_to_action_frame()

    except:
        messagebox.showerror("Connection", "Unable to connect")
        exit(0)

# Uploading process
def upload_file():
    # Tkinter's file dialog
    file_name = filedialog.askopenfilename(title = "Select a file to upload").strip()
    if not file_name:
        return # not file_name -> no file is selected
    file_size = str(os.path.getsize(file_name))

    try:
        sock.send(b"upload")
    
        metadata = json.dumps({
             "file_name": os.path.basename(file_name),
             "file_size": file_size
             })

        sock.send(metadata.encode())

        ack = sock.recv(1024).decode().strip()
        if ack != "ACK":
            raise Exception("Upload", f"Server did not acknowledge the upload request")
            

        # Progress screen
        show_progress_screen("Uploading")
    
        with open(file_name, "rb") as file:
            sent_size = 0
            while chunk := file.read(1024):
                sock.send(chunk)
                sent_size += len(chunk)
                update_progress(sent_size, int(file_size))
        
        ack = sock.recv(1024).decode().strip()
        if ack != "ACK":
            raise Exception("Upload", f"Upload failed")
            
        close_progress_screen()

        messagebox.showinfo("Upload", f"File '{file_name}' uploaded successfully")

    except Exception as e:
        close_progress_screen()
        messagebox.showerror("Upload", f"Error during upload: {e}")

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


def socket_exit():
    if socket_is_connected:
        sock.send(b"disconnect")
        sock.close()

    root.quit()

# Toggle between default and custom IP address and port number
def toggle_ip():
    if ip_default_var.get():
        
        ip_entry.config(state="disabled")
        ip_var.set("Local host")

    else:
        ip_entry.config(state="normal")
        ip_is_default = False
        ip_var.set("")

def toggle_port():
    if port_default_var.get():
        port_entry.config(state="disabled")
        port_var.set(str(default_port))
    else:
        port_entry.config(state="normal")
        port_var.set("")


def show_progress_screen(action_string):
    global progress_screen, progress_bar, progress_label
    progress_screen = tk.Toplevel(root)
    progress_screen.title(action_string)
    progress_screen.geometry("300x100")
    progress_screen.resizable(False, False) # width, height -> fixed size
    progress_screen.transient(root) # progress_screen -> child of root
    progress_screen.grab_set() # progress_screen -> modal dialog -> block input to root

    progress_title = tk.Label(progress_screen, text=f"{action_string}, please wait...", font=("Arial", 12))
    progress_title.pack(pady=10)

    # Progress bar
    progress_bar = tk.ttk.Progressbar(progress_screen, orient="horizontal", length=200, mode="determinate")
    progress_bar.pack(pady=10)

    # Progress label
    progress_label = tk.Label(progress_screen, text="0%", font=("Arial", 10))
    progress_label.pack()

def update_progress(current, total):
    percentage = int((current / total) * 100)
    progress_bar["value"] = percentage
    progress_label.config(text=f"{percentage}%")
    progress_screen.update_idletasks() # idletasks is a special event flag -> update progress bar

def close_progress_screen():
    if progress_screen:
        progress_screen.destroy()

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

# IP address and port number setup

# Default value
ip_is_default = True # for local host
default_port = 9999

# String variables for IP address and port number
ip_var = tk.StringVar(value="Local host")
port_var = tk.StringVar(value=str(default_port))

# Boolean variable for checkbox state
ip_default_var = tk.BooleanVar(value=True)
port_default_var = tk.BooleanVar(value=True)

# Checkbox to toggle between default and custom IP address and port number


# Tkinter's layout
# Connect frame
# IP address checkbox
ip_default_checkbox = tk.Checkbutton(
    connect_frame,
    text="Use default (local host)",
    variable=ip_default_var,
    command=lambda: toggle_ip(),
    anchor = "w" # text alignment in widget -> west: center left
)
ip_default_checkbox.place(x=btnX + btn_width, y=120, width=btn_width, height=30)

# IP address label
ip_label = tk.Label(connect_frame, text="Server IP address")
ip_label.place(x=btnX, y=90, width=btn_width, height=30)

# IP address entry
ip_entry = tk.Entry(connect_frame, textvariable=ip_var, state="disabled")
ip_entry.place(x=btnX, y=120, width=btn_width, height=30)

# Port number checkbox
port_default_checkbox = tk.Checkbutton(
    connect_frame,
    text=f"Use default ({str(default_port)})",
    variable=port_default_var,
    command=lambda: toggle_port(),
    anchor = "w" # text alignment in widget -> west: center left
)
port_default_checkbox.place(x=btnX + btn_width, y=180, width=btn_width, height=30)

# Port number label
port_label = tk.Label(connect_frame, text="Server port number")
port_label.place(x=btnX, y=150, width=btn_width, height=30)

# Port number entry
port_entry = tk.Entry(connect_frame, textvariable=port_var, state="disabled")
port_entry.place(x=btnX, y=180, width=btn_width, height=30)

# Connect button
connect_btn = tk.Button(connect_frame, text="Connect to Server", command=connect_to_server)
connect_btn.place(x=btnX, y=210, width=btn_width, height=btn_height)

# Exit button
exit_btn = tk.Button(connect_frame, text="Exit", command=socket_exit) # Tkinter's root.quit
exit_btn.place(x=btnX, y=260, width=btn_width, height=btn_height)


# Action frame
# Upload button
upload_btn = tk.Button(action_frame, text="Upload File", command=upload_file)
upload_btn.place(x=btnX, y=125, width=btn_width, height=btn_height)

# Download button
download_btn = tk.Button(action_frame, text="Download File", command=download_file)
download_btn.place(x=btnX, y=175, width=btn_width, height=btn_height)

# Exit button
exit_btn = tk.Button(action_frame, text="Exit", command=socket_exit) # Tkinter's root.quit
exit_btn.place(x=btnX, y=225, width=btn_width, height=btn_height)

# Tkinter's main event loop
root.mainloop()