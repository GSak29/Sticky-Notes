import tkinter as tk
from tkinter import messagebox, simpledialog
import os

# ================= UI SETTINGS (CUSTOMIZE HERE) =================
APP_WIDTH = 820
APP_HEIGHT = 480
MIN_WIDTH = 720
MIN_HEIGHT = 420

FONT_MAIN = ("Segoe UI", 11)
FONT_EDITOR = ("Segoe UI", 12)

BG = "#000000"
PANEL = "#0B0B0B"
TEXT_BG = "#effbff"
TEXT_COLOR = "#000000"
ACCENT = "#00b7ff"
LIST_HOVER_ACC = "#000000"
LIST_BG = "#9baebc"
BTN_HOVER = "#0095cc"
# =================================================================

NOTES_FOLDER = "my_notes"
if not os.path.exists(NOTES_FOLDER):
    os.makedirs(NOTES_FOLDER)

current_file = None

# ================= FUNCTIONS =================
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
        messagebox.showwarning("Empty", "Note is empty!", parent=root)
        return

    if current_file is None:
        name = simpledialog.askstring(
            "File Name", "Enter note name:", parent=root
        )
        if not name:
            return

        if not name.endswith(".txt"):
            name += ".txt"

        if os.path.exists(os.path.join(NOTES_FOLDER, name)):
            messagebox.showerror("Error", "File already exists!", parent=root)
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
    confirm = messagebox.askyesno(
        "Delete", f"Delete '{file_name}'?", parent=root
    )
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
        messagebox.showwarning("Select", "Select a note first.", parent=root)
        return

    old_name = notes_list.get(selection[0])
    new_name = simpledialog.askstring(
        "Rename", "Enter new file name:", parent=root
    )

    if not new_name:
        return

    if not new_name.endswith(".txt"):
        new_name += ".txt"

    if os.path.exists(os.path.join(NOTES_FOLDER, new_name)):
        messagebox.showerror("Error", "File already exists!", parent=root)
        return

    os.rename(
        os.path.join(NOTES_FOLDER, old_name),
        os.path.join(NOTES_FOLDER, new_name)
    )

    current_file = new_name
    refresh_notes()

# ================= UI =================
root = tk.Tk()
root.title("Sticky Notes Widget")
root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
root.minsize(MIN_WIDTH, MIN_HEIGHT)   # ⭐ prevents hiding buttons
root.configure(bg=BG)
root.attributes("-topmost", True)
root.resizable(True, True)            # ⭐ allow resizing

# Grid layout (stable resizing)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

main_frame = tk.Frame(root, bg=BG)
main_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Left panel
left_frame = tk.Frame(main_frame, bg=PANEL, width=220)
left_frame.grid(row=0, column=0, sticky="ns", padx=(0, 12))

left_frame.grid_rowconfigure(1, weight=1)

tk.Label(
    left_frame, text="📝 My Notes",
    bg=PANEL, fg="white",
    font=("Segoe UI", 13, "bold")
).grid(row=0, column=0, pady=10)

notes_list = tk.Listbox(
    left_frame,
    bg=LIST_BG,
    fg="white",
    selectbackground=LIST_HOVER_ACC,
    selectforeground="white",
    activestyle="none", 
    font=FONT_MAIN,
    relief="flat",
    highlightthickness=0
)
notes_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
notes_list.bind("<<ListboxSelect>>", open_note)

# Right panel
right_frame = tk.Frame(main_frame, bg=PANEL)
right_frame.grid(row=0, column=1, sticky="nsew")

right_frame.grid_rowconfigure(0, weight=1)

text_area = tk.Text(
    right_frame,
    bg=TEXT_BG,
    fg=TEXT_COLOR,
    insertbackground="white",
    font=FONT_EDITOR,
    relief="flat",
    padx=14,
    pady=14
)
text_area.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 6))

# Buttons (always visible)
btn_frame = tk.Frame(right_frame, bg=PANEL)
btn_frame.grid(row=1, column=0, sticky="ew", pady=8)

def create_button(parent, text, cmd):
    btn = tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=ACCENT,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=14,
        pady=6,
        cursor="hand2",
        activebackground=BTN_HOVER
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))
    return btn

create_button(btn_frame, "🗒️New", new_note).pack(side="left", padx=6)
create_button(btn_frame, "💾 Save", save_note).pack(side="left", padx=6)
create_button(btn_frame, "📝 Rename", rename_note).pack(side="left", padx=6)
create_button(btn_frame, "🗑 Delete", delete_note).pack(side="left", padx=6)

refresh_notes()
root.mainloop()
