import tkinter as tk
from tkinter import ttk, colorchooser, simpledialog, messagebox

class ResizableFrame(tk.Frame):
    def __init__(self, parent, width=200, height=150, bg="gray", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, **kwargs)
        self.parent = parent
        self.pack_propagate(False)
        self.bg_color = bg
        
        # Context Menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Properties", command=self.show_properties)
        self.menu.add_command(label="Delete", command=self.delete_widget)

        # Bindings
        self.bind("<Button-3>", self.show_menu)
        
        # Resize handle
        self.sizer = tk.Frame(self, bg="#444", width=10, height=10, cursor="sizing")
        self.sizer.place(relx=1.0, rely=1.0, anchor="se")
        self.sizer.bind("<B1-Motion>", self.do_resize)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def do_resize(self, event):
        w, h = self.winfo_width(), self.winfo_height()
        new_w = w + event.x
        new_h = h + event.y
        if new_w > 50 and new_h > 50:
            self.config(width=new_w, height=new_h)
            
            # Since this is embedded in a text widget, we might need to update the window_configure
            # But usually, just resizing the frame is enough if the Text widget knows it's a window.
            # However, for smooth interaction inside a tk.Text, we often need to re-configure the window size via the Text widget method if exact control is needed.
            # For this simple implementation, direct config works but might be slightly jittery.

    def show_properties(self):
        pass

    def delete_widget(self):
        self.destroy()

class CardWidget(ResizableFrame):
    def __init__(self, parent, title="Title", content="Content", bg="#333333", fg="#ffffff", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.title_var = tk.StringVar(value=title)
        
        # Header Frame
        self.header_frame = tk.Frame(self, bg=bg, height=25)
        self.header_frame.pack(fill="x", side="top", padx=0, pady=0)
        self.header_frame.pack_propagate(False)

        # Title Entry
        self.lbl_title = tk.Entry(self.header_frame, textvariable=self.title_var, bg=bg, fg=fg, font=("Consolas", 10, "bold"), bd=0, relief="flat")
        self.lbl_title.pack(side="left", fill="both", expand=True, padx=5)
        
        # Color Button
        self.btn_color = tk.Button(self.header_frame, text="🎨", command=self.choose_color, font=("Consolas", 9), bg=bg, fg=fg, relief="flat", bd=0, width=3)
        self.btn_color.pack(side="right", padx=0)
        
        self.text_body = tk.Text(self, bg=bg, fg=fg, font=("Consolas", 10), relief="flat", wrap="word", padx=5, pady=5)
        self.text_body.insert("1.0", content)
        self.text_body.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        
        self.text_body.bind("<Button-3>", self.show_menu)
        self.lbl_title.bind("<Button-3>", self.show_menu)
        self.sizer.lift()

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Card Color", initialcolor=self.bg_color)[1]
        if color:
            self.configure_color(color)

    def configure_color(self, color):
        self.configure(bg=color)
        self.header_frame.configure(bg=color)
        self.lbl_title.configure(bg=color)
        self.btn_color.configure(bg=color)
        self.text_body.configure(bg=color)
        self.bg_color = color

    def show_properties(self):
        self.choose_color()

    def get_data(self):
        return {
            "type": "card",
            "width": self.winfo_width(),
            "height": self.winfo_height(),
            "title": self.title_var.get(),
            "content": self.text_body.get("1.0", "end-1c"),
            "bg": self.bg_color
        }

class TableWidget(ResizableFrame):
    def __init__(self, parent, rows=3, cols=3, cell_width=10, cell_height=1, align="center", **kwargs):
        super().__init__(parent, **kwargs)
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width  # Can be int, str, or list
        self.cell_height = cell_height
        self.align = align  # "left", "center", "right"
        self.cells = []
        
        self.menu.add_command(label="Settings", command=self.show_properties)

        # Header for Settings
        self.header_frame = tk.Frame(self, bg=self.bg_color, height=20)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.btn_delete = tk.Button(self.header_frame, text="❌", command=self.delete_widget, font=("Consolas", 9), bg=self.bg_color, relief="flat", bd=0, width=3)
        self.btn_delete.pack(side="right", padx=0)

        self.btn_settings = tk.Button(self.header_frame, text="🛠", command=self.show_properties, font=("Consolas", 9), bg=self.bg_color, relief="flat", bd=0, width=3)
        self.btn_settings.pack(side="right", padx=2)

        self.grid_frame = tk.Frame(self, bg=self.bg_color)
        self.grid_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.build_table()

    def build_table(self):
        # 1. Preserve existing data
        old_data = []
        # Check if cells exist (first run they don't)
        if hasattr(self, 'cells') and self.cells:
             # get_data returns a dict, we need the 'data' list from it
             # But self.get_data() relies on self.rows/cols which might have just changed if this is called after updating attributes?
             # Actually get_data uses len(self.cells), so it's safe to call on *current* state.
             try:
                 old_data = self.get_data().get("data", [])
             except:
                 old_data = []

        # Clear existing
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        self.cells = []
        justify_map = {"left": "left", "center": "center", "right": "right"}
        justify_val = justify_map.get(self.align, "center")
        
        # Ensure sizer is on top
        self.sizer.lift()

        # Reset grid weights for unused columns to prevent ghost spacing
        for i in range(20):
             self.grid_frame.grid_columnconfigure(i, weight=0)

        # Parse widths
        widths = []
        try:
            if isinstance(self.cell_width, list):
                widths = self.cell_width
            elif isinstance(self.cell_width, str) and "," in self.cell_width:
                widths = [int(w.strip()) for w in self.cell_width.split(",")]
            else:
                widths = [int(self.cell_width)]
        except:
            widths = [10] # Fallback

        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                # Determine width for this column
                w = widths[c % len(widths)]
                
                e = tk.Entry(self.grid_frame, bg="#ffffff", fg="#000000", relief="solid", bd=1, justify=justify_val, font=("Consolas", 10))
                e.configure(width=w)
                
                e.grid(row=r, column=c, sticky="nsew", padx=0, pady=0)
                
                self.grid_frame.grid_rowconfigure(r, weight=1)
                self.grid_frame.grid_columnconfigure(c, weight=1)
                
                e.bind("<Button-3>", lambda event: self.menu.post(event.x_root, event.y_root))
                
                # Restore data if available
                if r < len(old_data) and c < len(old_data[r]):
                    e.insert(0, old_data[r][c])

                row_cells.append(e)
            self.cells.append(row_cells)

    def show_properties(self):
        # Dialog to edit settings
        win = tk.Toplevel(self)
        win.title("Table Settings")
        win.geometry("300x300")
        win.transient(self)
        win.grab_set()
        
        def create_input(label, var):
            f = tk.Frame(win)
            f.pack(fill="x", padx=10, pady=5)
            tk.Label(f, text=label, width=15, anchor="w").pack(side="left")
            tk.Entry(f, textvariable=var).pack(side="right", fill="x", expand=True)

        rows_var = tk.IntVar(value=self.rows)
        cols_var = tk.IntVar(value=self.cols)
        # Use simple string var for width to allow csv
        width_var = tk.StringVar(value=str(self.cell_width).replace("[", "").replace("]", "").replace("'", "")) 
        align_var = tk.StringVar(value=self.align)

        create_input("Rows:", rows_var)
        create_input("Columns:", cols_var)
        create_input("Widths (csv):", width_var)
        
        # Alignment
        f_align = tk.Frame(win)
        f_align.pack(fill="x", padx=10, pady=5)
        tk.Label(f_align, text="Alignment:", width=15, anchor="w").pack(side="left")
        align_cb = ttk.Combobox(f_align, textvariable=align_var, values=["left", "center", "right"])
        align_cb.pack(side="right", fill="x", expand=True)

        def apply():
            try:
                self.rows = rows_var.get()
                self.cols = cols_var.get()
                
                # Check if width is list format or single int
                w_str = width_var.get()
                if "," in w_str:
                     self.cell_width = w_str # Keep as string for persistence/re-parsing
                else:
                     self.cell_width = int(w_str)

                self.align = align_var.get()
                self.build_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(win, text="Apply", command=apply).pack(pady=20)

    def get_data(self):
        data = []
        for r in range(len(self.cells)):
            row_data = []
            for c in range(len(self.cells[r])):
                row_data.append(self.cells[r][c].get())
            data.append(row_data)
        
        return {
            "type": "table",
            "width": self.winfo_width(),
            "height": self.winfo_height(),
            "rows": self.rows,
            "cols": self.cols,
            "cell_width": self.cell_width,
            "align": self.align,
            "data": data,
            "bg": self.bg_color
        }
