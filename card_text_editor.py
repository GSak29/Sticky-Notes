import tkinter as tk

class CardTextEditor(tk.Frame):
    """
    A text editor widget with card-like layout support.
    You can simulate columns or colored cards inside a scrollable frame.
    """
    def __init__(self, parent, bg="#effbff", text_color="#000000",
                 font=("Segoe UI", 12), card_bg="#ffffff", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        
        self.card_bg = card_bg

        # Scrollable canvas for cards
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Frame inside canvas
        self.inner_frame = tk.Frame(self.canvas, bg=bg)
        self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Keep track of cards
        self.cards = []

        # Default font and colors
        self.font = font
        self.text_color = text_color

    def add_card(self, content=""):
        """Add a new card (like a column)"""
        card = tk.Text(
            self.inner_frame,
            bg=self.card_bg,
            fg=self.text_color,
            font=self.font,
            relief="raised",
            bd=2,
            padx=10,
            pady=10,
            width=30,
            height=10
        )
        card.insert("1.0", content)
        card.pack(padx=10, pady=10, side="left")
        self.cards.append(card)
        return card

    def get_all_texts(self):
        """Return all card texts as a list"""
        return [c.get("1.0", "end").strip() for c in self.cards]

    def clear_all(self):
        """Clear all cards"""
        for c in self.cards:
            c.destroy()
        self.cards.clear()
