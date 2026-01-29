import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label, Button
import os
import json
from theme_manager import ThemeManager
from rich_text_editor import RichTextEditor

# ================= UI SETTINGS =================
APP_WIDTH = 900
APP_HEIGHT = 600
MIN_WIDTH = 800
MIN_HEIGHT = 500
NOTES_FOLDER = "my_notes"

if not os.path.exists(NOTES_FOLDER):
    os.makedirs(NOTES_FOLDER)

class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Sticky Notes")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Could not load icon: {e}")
        
        self.tm = ThemeManager()
        self.current_file = None
        
        self.setup_ui()
        self.apply_theme()
        self.refresh_notes()

        self.setup_ui()
        self.apply_theme()
        self.refresh_notes()
        self.create_sidebar_context_menu()
        
        self.last_saved_content = []  # Track saved state
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Main Grid
        self.root.grid_rowconfigure(1, weight=1) # Main content area
        self.root.grid_columnconfigure(0, weight=0) # Sidebar
        self.root.grid_columnconfigure(1, weight=1) # Editor
        
        # --- Toolbar (Top) ---
        self.toolbar = tk.Frame(self.root, height=40)
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.toolbar.pack_propagate(False)
        
        # Toolbar Buttons
        self.btn_new = tk.Button(self.toolbar, text="New Note", command=self.new_note, relief="flat", padx=10, font=("Consolas", 10))
        self.btn_new.pack(side="left", padx=2, pady=2)
        
        self.btn_save = tk.Button(self.toolbar, text="Save", command=self.save_note, relief="flat", padx=10, font=("Consolas", 10))
        self.btn_save.pack(side="left", padx=2, pady=2)

        self.btn_card = tk.Button(self.toolbar, text="+ Card", command=lambda: self.editor.insert_card(), relief="flat", padx=10, font=("Consolas", 10))
        self.btn_card.pack(side="left", padx=10, pady=2)

        self.btn_table = tk.Button(self.toolbar, text="+ Table", command=lambda: self.editor.insert_table(), relief="flat", padx=10, font=("Consolas", 10))
        self.btn_table.pack(side="left", padx=2, pady=2)

        self.btn_settings = tk.Button(self.toolbar, text="Settings", command=self.open_settings, relief="flat", padx=10, font=("Consolas", 10))
        self.btn_settings.pack(side="right", padx=2, pady=2)

        # --- Sidebar (Left) ---
        self.sidebar = tk.Frame(self.root, width=220)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.sidebar.pack_propagate(False) # Force width
        
        self.lbl_notes = tk.Label(self.sidebar, text="My Notes", font=("Consolas", 12, "bold"))
        self.lbl_notes.pack(fill="x", pady=5, padx=5)

        self.notes_list = tk.Listbox(self.sidebar, font=("Consolas", 10), bd=0, highlightthickness=0)
        self.notes_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.notes_list.bind("<<ListboxSelect>>", self.open_note)
        
        # --- Editor (Right) ---
        self.editor_frame = tk.Frame(self.root)
        self.editor_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        self.editor = RichTextEditor(self.editor_frame, font=("Consolas", 11), wrap="word", relief="flat", padx=10, pady=10)
        self.editor.pack(fill="both", expand=True)

    def apply_theme(self):
        colors = self.tm.colors
        bg = colors["bg"]
        fg = colors["fg"]
        panel = colors["panel_bg"]
        toolbar_bg = colors.get("toolbar_bg", panel)
        accent = colors["accent"]
        
        self.root.configure(bg=bg)
        self.toolbar.configure(bg=toolbar_bg)
        self.sidebar.configure(bg=panel)
        self.editor_frame.configure(bg=bg)
        
        # Buttons
        for btn in self.toolbar.winfo_children():
            btn.configure(bg=accent, fg="#ffffff", activebackground=colors.get("list_select", "#444"))
            
        # Lists and Labels
        self.lbl_notes.configure(bg=panel, fg=fg)
        self.notes_list.configure(
            bg=colors["list_bg"], 
            fg=colors["list_fg"],
            selectbackground=colors["list_select"],
            selectforeground=colors["list_fg"]
        )
        
        # Editor
        self.editor.configure(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=fg)

    def refresh_notes(self):
        self.notes_list.delete(0, tk.END)
        for file in sorted(os.listdir(NOTES_FOLDER)):
            if file.endswith(".json"):
                self.notes_list.insert(tk.END, file.replace(".json", ""))

    def new_note(self):
        if self.check_unsaved_changes():
            self.current_file = None
            self.editor.delete("1.0", tk.END)
            self.editor.widgets.clear()
            self.last_saved_content = []

    def save_note(self):
        content = self.editor.get_content_json()
        
        if self.current_file is None:
            name = simpledialog.askstring("Save Note", "Enter note name:", parent=self.root)
            if not name: return
            self.current_file = name
        
        file_path = os.path.join(NOTES_FOLDER, self.current_file + ".json")
        try:
            with open(file_path, "w") as f:
                json.dump(content, f, indent=2)
            self.refresh_notes()
            self.last_saved_content = content
            messagebox.showinfo("Saved", "Note saved successfully!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}", parent=self.root)

    def open_note(self, event):
        if not self.check_unsaved_changes():
            return

        selection = self.notes_list.curselection()
        if not selection: return
        
        note_name = self.notes_list.get(selection[0])
        self.current_file = note_name
        file_path = os.path.join(NOTES_FOLDER, note_name + ".json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    content = json.load(f)
                self.editor.load_content_json(content)
                self.last_saved_content = content
                self.last_saved_content = content
            except Exception as e:
                messagebox.showerror("Error", f"Could not open note: {e}")

    def create_sidebar_context_menu(self):
        self.sidebar_menu = tk.Menu(self.root, tearoff=0)
        self.sidebar_menu.add_command(label="Rename", command=self.rename_note)
        self.sidebar_menu.add_command(label="Delete", command=self.delete_note)
        
        self.notes_list.bind("<Button-3>", self.show_sidebar_menu)

    def show_sidebar_menu(self, event):
        # Select the item under cursor
        try:
            self.notes_list.selection_clear(0, tk.END)
            self.notes_list.selection_set(self.notes_list.nearest(event.y))
            self.notes_list.activate(self.notes_list.nearest(event.y))
            self.sidebar_menu.post(event.x_root, event.y_root)
        except:
            pass

    def rename_note(self):
        selection = self.notes_list.curselection()
        if not selection: return
        old_name = self.notes_list.get(selection[0])
        
        new_name = simpledialog.askstring("Rename Note", "Enter new name:", initialvalue=old_name, parent=self.root)
        if new_name and new_name != old_name:
            old_path = os.path.join(NOTES_FOLDER, old_name + ".json")
            new_path = os.path.join(NOTES_FOLDER, new_name + ".json")
            try:
                os.rename(old_path, new_path)
                self.refresh_notes()
                if self.current_file == old_name:
                    self.current_file = new_name
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename: {e}")

    def delete_note(self):
        selection = self.notes_list.curselection()
        if not selection: return
        name = self.notes_list.get(selection[0])
        
        if messagebox.askyesno("Delete Note", f"Are you sure you want to delete '{name}'?", parent=self.root):
            path = os.path.join(NOTES_FOLDER, name + ".json")
            try:
                os.remove(path)
                self.refresh_notes()
                if self.current_file == name:
                    self.new_note() # Clear editor if we deleted open note
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")

    def check_unsaved_changes(self):
        """Returns True if it's safe to proceed (saved or discarded), False if cancelled."""
        current_content = self.editor.get_content_json()
        if current_content != self.last_saved_content:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them?", parent=self.root)
            if response is True: # Yes
                self.save_note()
                return True
            elif response is False: # No
                return True # User chose NOT to save, so we proceed
            else: # Cancel (None)
                return False
        return True

    def on_closing(self):
        if self.check_unsaved_changes():
            self.root.destroy()

    def open_settings(self):
        win = Toplevel(self.root)
        win.title("Settings")
        win.geometry("300x200")
        win.configure(bg=self.tm.get_color("panel_bg"))
        
        Label(win, text="Select Theme", bg=self.tm.get_color("panel_bg"), fg=self.tm.get_color("fg"), font=("Segoe UI", 12)).pack(pady=10)
        
        def set_theme(name):
            self.tm.set_theme(name)
            self.apply_theme()
            win.destroy()

        Button(win, text="Dark Mode", command=lambda: set_theme("Dark"), width=20, pady=5).pack(pady=5)
        Button(win, text="Light Mode", command=lambda: set_theme("Light"), width=20, pady=5).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()
