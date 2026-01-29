import tkinter as tk
from tkinter import messagebox
from widgets import CardWidget, TableWidget

class RichTextEditor(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.widgets = {}  # Map window name -> Widget instance

    def insert_card(self):
        try:
            card = CardWidget(self, width=200, height=120)
            self.window_create("insert", window=card, padx=5, pady=5)
            self.widgets[str(card)] = card
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert card: {e}")

    def insert_table(self):
        try:
            # Create default 3x3 table immediately
            table = TableWidget(self, rows=3, cols=3, cell_width=10, align="center", width=300, height=150)
            self.window_create("insert", window=table, padx=0, pady=2)
            self.widgets[str(table)] = table
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert table: {e}")

    def get_content_json(self):
        """
        Serializes the content into a list of segments.
        Each segment is either {"type": "text", "content": "..."} or a widget dict.
        """
        content = []
        
        # We use 'dump' to get everything in order
        # dump returns tuples: (key, value, index)
        # key is 'text', 'mark', 'tagon', 'tagoff', 'window', 'image'
        try:
            # "1.0" to "end-1c" (exclude trailing newline)
            elements = self.dump("1.0", "end-1c", text=True, window=True)
            
            if not elements:
                return []

            for key, value, index in elements:
                if key == "text":
                    content.append({"type": "text", "content": value})
                elif key == "window":
                    # value is the window name (string path)
                    # We need to find the widget object
                    # Tkinter widget paths are unique strings.
                    # We stored mapping in self.widgets, BUT window names might change or be tricky.
                    # Best way: self.nametowidget(value)
                    try:
                        widget = self.nametowidget(value)
                        if isinstance(widget, (CardWidget, TableWidget)):
                            content.append(widget.get_data())
                    except KeyError:
                        pass # Widget might have been destroyed but still in dump? Unlikely.
        except Exception as e:
            print(f"Error saving: {e}")
            
        return content

    def load_content_json(self, content_list):
        self.delete("1.0", tk.END)
        self.widgets.clear()
        
        if not content_list:
            return

        for item in content_list:
            if item.get("type") == "text":
                self.insert("end", item.get("content", ""))
            elif item.get("type") == "card":
                card = CardWidget(
                    self, 
                    title=item.get("title", ""), 
                    content=item.get("content", ""),
                    bg=item.get("bg", "#333333"),
                    width=item.get("width", 200),
                    height=item.get("height", 120)
                )
                self.window_create("end", window=card, padx=5, pady=5)
                self.widgets[str(card)] = card
            elif item.get("type") == "table":
                table = TableWidget(
                    self,
                    rows=item.get("rows", 3),
                    cols=item.get("cols", 3),
                    cell_width=item.get("cell_width", 10),
                    align=item.get("align", "center"),
                    width=item.get("width", 300),
                    height=item.get("height", 150),
                    bg=item.get("bg", "gray")
                )
                # Restore cell data
                saved_data = item.get("data", [])
                if saved_data:
                    for r, row_vals in enumerate(saved_data):
                        if r < len(table.cells):
                            for c, val in enumerate(row_vals):
                                if c < len(table.cells[r]):
                                    table.cells[r][c].insert(0, val)
                
                self.window_create("end", window=table, padx=5, pady=5)
                self.widgets[str(table)] = table
