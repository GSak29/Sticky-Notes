import tkinter as tk
from tkinter import messagebox, simpledialog
import os

NOTES_FOLDER = "my_notes"

if not os.path.exists(NOTES_FOLDER):
    os.makedirs(NOTES_FOLDER)

current_file = None

def refresh_notes():
    notes_list.delete(0, tk.END)
    for file in sorted(os.listdir(NOTES_FOLDER)):
        if file.endswith(".txt"):
            notes_list.insert(tk.END, file)

def new_note():
    global current_file
    current_file = None
    text_area.delete("1.0", tk.END)

def save_note():
    global current_file
    content = text_area.get("1.0", tk.END).strip()

    if not content:
        messagebox.showwarning("Empty", "Note is empty!")
        return

    if current_file is None:
        name = simpledialog.askstring("File Name", "Enter note name:")
        if not name:
            return
        if not name.endswith(".txt"):
            name += ".txt"

        if os.path.exists(os.path.join(NOTES_FOLDER, name)):
            messagebox.showerror("Error", "File already exists!")
            return

        current_file = name

    with open(os.path.join(NOTES_FOLDER, current_file), "w", encoding="utf-8") as f:
        f.write(content)

    refresh_notes()

def open_note(event):
    global current_file
    selection = notes_list.curselection()
    if not selection:
        return

    file_name = notes_list.get(selection[0])
    current_file = file_name

    with open(os.path.join(NOTES_FOLDER, file_name), "r", encoding="utf-8") as f:
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", f.read())

def delete_note():
    global current_file
    selection = notes_list.curselection()
    if not selection:
        return

    file_name = notes_list.get(selection[0])
    confirm = messagebox.askyesno("Delete", f"Delete '{file_name}'?")
    if not confirm:
        return

    os.remove(os.path.join(NOTES_FOLDER, file_name))
    current_file = None
    text_area.delete("1.0", tk.END)
    refresh_notes()

def rename_note():
    global current_file
    selection = notes_list.curselection()
    if not selection:
        messagebox.showwarning("Select", "Select a note first.")
        return

    old_name = notes_list.get(selection[0])
    new_name = simpledialog.askstring("Rename", "Enter new file name:")

    if not new_name:
        return

    if not new_name.endswith(".txt"):
        new_name += ".txt"

    if os.path.exists(os.path.join(NOTES_FOLDER, new_name)):
        messagebox.showerror("Error", "File already exists!")
        return

    os.rename(
        os.path.join(NOTES_FOLDER, old_name),
        os.path.join(NOTES_FOLDER, new_name)
    )

    current_file = new_name
    refresh_notes()

root = tk.Tk()
root.title("My Sticky Notes")
root.geometry("700x420")
root.attributes("-topmost", True)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

left_frame = tk.Frame(main_frame, width=200)
left_frame.pack(side="left", fill="y")

notes_list = tk.Listbox(left_frame)
notes_list.pack(fill="both", expand=True, padx=5, pady=5)
notes_list.bind("<<ListboxSelect>>", open_note)

right_frame = tk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True)

text_area = tk.Text(right_frame, font=("Arial", 12))
text_area.pack(fill="both", expand=True, padx=5, pady=(5, 0))

btn_frame = tk.Frame(right_frame)
btn_frame.pack(fill="x", pady=5)

tk.Button(btn_frame, text="🆕 New", command=new_note).pack(side="left", padx=5)
tk.Button(btn_frame, text="💾 Save", command=save_note).pack(side="left", padx=5)
tk.Button(btn_frame, text="✏️ Rename", command=rename_note).pack(side="left", padx=5)
tk.Button(btn_frame, text="🗑 Delete", command=delete_note).pack(side="left", padx=5)

refresh_notes()
root.mainloop()
