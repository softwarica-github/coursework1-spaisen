import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext
import sqlite3
from fleep import get
import os

MONONOKI_NERD_FONT = ("Mononoki Nerd Font", 12)

def get_file_extension_with_fleep(file_path):
    with open(file_path, 'rb') as file:
        info = get(file.read(128))
        return info.extension or "Unknown"

def create_database():
    connection = sqlite3.connect("log.db")
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS file_log 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT, renamed_name TEXT)''')
    connection.commit()
    connection.close()

def log_rename(original_name, renamed_name):
    connection = sqlite3.connect("log.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO file_log (original_name, renamed_name) VALUES (?, ?)", (original_name, renamed_name))
    connection.commit()
    connection.close()

def browse_file():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("All Files", "*.*")])
    entry_path.delete(0, tk.END)
    entry_path.insert(0, file_path)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Click 'Reveal' to show file extension.")
    result_text.config(state=tk.DISABLED)

def reveal_file_extension():
    file_path = entry_path.get()

    if not file_path or not file_path.strip():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Invalid file path.")
        result_text.config(state=tk.DISABLED)
        return

    extension_list = get_file_extension_with_fleep(file_path)

    if extension_list:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"The detected file extension is: {extension_list}")
        result_text.config(state=tk.DISABLED)
    else:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "File extension not found.")
        result_text.config(state=tk.DISABLED)

def rename_file():
    file_path = entry_path.get()

    if not file_path or not file_path.strip():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Invalid file path.")
        result_text.config(state=tk.DISABLED)
        return

    selected_name = ask_for_new_name()

    if selected_name:
        original_name = os.path.basename(file_path)
        new_file_path = os.path.join(os.path.dirname(file_path), selected_name)
        os.rename(file_path, new_file_path)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"File renamed to: {new_file_path}")
        result_text.config(state=tk.DISABLED)
        log_rename(original_name, os.path.basename(new_file_path))
    else:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "File not renamed.")
        result_text.config(state=tk.DISABLED)

def undo_rename():
    file_path = entry_path.get()

    if not file_path or not file_path.strip():
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Invalid file path.")
        result_text.config(state=tk.DISABLED)
        return

    original_name = os.path.basename(file_path)

    connection = sqlite3.connect("log.db")
    cursor = connection.cursor()

    cursor.execute("SELECT original_name FROM file_log WHERE renamed_name=?", (original_name,))
    original_name_result = cursor.fetchone()

    if original_name_result:
        original_name = original_name_result[0]
        new_file_path = os.path.join(os.path.dirname(file_path), original_name)
        os.rename(file_path, new_file_path)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Undo: File reverted to original path: {new_file_path}")
        result_text.config(state=tk.DISABLED)
    else:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No renaming operation to undo.")
        result_text.config(state=tk.DISABLED)

def ask_for_new_name():
    selected_name = simpledialog.askstring("Enter New Name", "Enter the desired file name (with extension):", initialvalue=os.path.basename(entry_path.get()))
    return selected_name

def read_log():
    connection = sqlite3.connect("log.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM file_log")
    changes = cursor.fetchall()
    connection.close()

    if not changes:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No changes in the log.")
        result_text.config(state=tk.DISABLED)
        return

    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Changes in the log:\n")
    for change in changes:
        result_text.insert(tk.END, f"{change[1]} -> {change[2]}\n")
    result_text.config(state=tk.DISABLED)

create_database()

#GUI
root = tk.Tk()
root.title("File Extension Manager")

label_path = tk.Label(root, text="File Path:", font=MONONOKI_NERD_FONT)
label_path.grid(row=0, column=0, padx=10, pady=10, sticky="e")

entry_path = tk.Entry(root, width=50, font=MONONOKI_NERD_FONT)
entry_path.grid(row=0, column=1, padx=10, pady=10, sticky="w")

browse_button = tk.Button(root, text="Browse", command=browse_file, font=MONONOKI_NERD_FONT)
browse_button.grid(row=0, column=2, padx=10, pady=10)

reveal_button = tk.Button(root, text="Reveal", command=reveal_file_extension, font=MONONOKI_NERD_FONT)
reveal_button.grid(row=1, column=0, padx=10, pady=10)

rename_button = tk.Button(root, text="Rename", command=rename_file, font=MONONOKI_NERD_FONT)
rename_button.grid(row=1, column=1, padx=10, pady=10)

undo_button = tk.Button(root, text="Undo", command=undo_rename, font=MONONOKI_NERD_FONT)
undo_button.grid(row=1, column=2, padx=10, pady=10)

read_log_button = tk.Button(root, text="Read Log", command=read_log, font=MONONOKI_NERD_FONT)
read_log_button.grid(row=2, column=0, columnspan=3, pady=10)

result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=10, font=MONONOKI_NERD_FONT)
result_text.grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
