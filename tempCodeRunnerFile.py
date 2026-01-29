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
