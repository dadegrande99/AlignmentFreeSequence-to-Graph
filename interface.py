import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image, ImageTk
from alignmentfreegraph import AlignmentFreeGraph

# Variables
afg = None
selected_file = None

# Functions


def do_nothing():
    pass


def select_config_file():
    global selected_file
    selected_file = open_file_dialog_json()
    # controlla se il file scelta è nella stessa directory di interface.py, nel caso lo sia cancella il path e tieni solo il nominee

    file_label.configure(text=selected_file.split("/")[-1])


def open_file_dialog():
    # Use the global keyword to indicate that we want to use the global variable
    global selected_file
    selected_file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                               filetypes=[("json files", "*.json"), ("text files", "*.txt"), ("all files", "*.*")])
    # Do something with the filename
    return selected_file


def open_file_dialog_json():
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                          filetypes=[("json files", "*.json")])
    return filename


def is_file_in_current_directory(filename):
    files_in_directory = os.listdir('.')
    return filename in files_in_directory


def login():
    print("Login")
    location = location_entry.get()
    if location == "":
        location = None
    db_name = db_name_entry.get()
    if db_name == "":
        db_name = None
    username = username_entry.get()
    if username == "":
        username = None
    password = password_entry.get()
    if password == "":
        password = None

    global afg
    global selected_file

    print(selected_file)
    new_window.destroy()
    try:
        afg = AlignmentFreeGraph(
            location, db_name, username, password, selected_file)
        print("Connected")
        selected_file = None

    except Exception as e:
        new_connection(error=e)


def new_connection(message: str = "Create a conection", error: str = None):
    def close_window():
        new_window.destroy()
    global new_window
    new_window = ctk.CTkToplevel(master=root)
    new_window.title("New Connection")
    new_window.geometry("500x500")

    if afg is None:
        root.config(bg='gray')
        new_window.grab_set()
        # change the background color back to white when the new window is closed
        new_window.bind('<Destroy>', lambda e: root.config(bg=root_bg_color))
        new_window.protocol("WM_DELETE_WINDOW", do_nothing)
    else:
        new_window.protocol("WM_DELETE_WINDOW", close_window)

    message_label = ctk.CTkLabel(
        master=new_window, text=message, font=("Roboto", 16))
    message_label.pack()

    if error is not None:
        error_label = ctk.CTkLabel(
            master=new_window, text=error, text_color="red")
        error_label.pack()

    conn_bg_color = new_window.cget("bg")

    global file_label
    file_button = ctk.CTkButton(
        master=new_window, text="Connect by file", command=select_config_file, fg_color="#24a0ed", hover_color="#1183ca")
    file_button.pack(pady=10)

    file_label = ctk.CTkLabel(
        master=new_window, text="", font=("Consolas", 12))
    file_label.pack()

    global location_entry
    location_frame = ctk.CTkFrame(
        master=new_window, bg_color=conn_bg_color)
    location_label = ctk.CTkLabel(master=location_frame, text="Location")
    location_entry = ctk.CTkEntry(
        master=location_frame, placeholder_text="Location")

    global db_name_entry
    db_name_frame = ctk.CTkFrame(master=new_window, bg_color=conn_bg_color)
    db_name_label = ctk.CTkLabel(master=db_name_frame, text="DB Name")
    db_name_entry = ctk.CTkEntry(
        master=db_name_frame, placeholder_text="DB Name")

    global username_entry
    username_frame = ctk.CTkFrame(master=new_window, bg_color=conn_bg_color)
    username_label = ctk.CTkLabel(master=username_frame, text="Username")
    username_entry = ctk.CTkEntry(
        master=username_frame, placeholder_text="Username")

    global password_entry
    password_frame = ctk.CTkFrame(master=new_window, bg_color=conn_bg_color)
    password_label = ctk.CTkLabel(master=password_frame, text="Password")
    password_entry = ctk.CTkEntry(
        master=password_frame, show="*", placeholder_text="Password")

    location_label.pack(side="left", padx=5)
    location_entry.pack(side="left")
    location_frame.pack(pady=10)

    db_name_label.pack(side="left", padx=5)
    db_name_entry.pack(side="left")
    db_name_frame.pack(pady=10)

    username_label.pack(side="left", padx=5)
    username_entry.pack(side="left")
    username_frame.pack(pady=10)

    password_label.pack(side="left", padx=5)
    password_entry.pack(side="left")
    password_frame.pack(pady=10)

    login_button = ctk.CTkButton(
        master=new_window, text="Login", command=login,)
    login_button.pack(pady=30)


# Creating interface

# interface style
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# main window
root = ctk.CTk()
root.geometry("800x800")
root.minsize(500, 500)
root.maxsize(1000, 1000)
root_bg_color = root.cget("bg")

root.title("Alignment-Free Sequence to Graph")

# frame of the interface
frame = ctk.CTkFrame(master=root)
frame.pack(pady=10, padx=15, fill="both", expand=True)
open_window_button = ctk.CTkButton(
    master=frame, text="New Connection", command=new_connection)
open_window_button.pack(anchor="ne", pady=5, padx=10)
# Project title
title = ctk.CTkLabel(
    master=frame, text="Alignment-Free Sequence to Graph", font=("Roboto", 24))
title.pack(pady=5, padx=10)

if is_file_in_current_directory("credentials.json"):
    try:
        afg = AlignmentFreeGraph(configuration="credentials.json")
    except Exception as e:
        new_connection(error=e)


# Create a button that will close the interface when clicked

exit_button = ctk.CTkButton(
    master=frame, text="Exit", command=root.destroy, fg_color="#df2c14", hover_color="#c61a09")
exit_button.pack(side='bottom', pady=5, padx=10)


root.mainloop()
