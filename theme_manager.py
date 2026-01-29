import json
import os

THEME_FILE = "theme.json"

DEFAULT_THEMES = {
    "Dark": {
        "bg": "#000000",
        "fg": "#ffffff",
        "panel_bg": "#0B0B0B",
        "toolbar_bg": "#101010",
        "accent": "#007acc",
        "entry_bg": "#292929",
        "entry_fg": "#ffffff",
        "list_bg": "#000000",
        "list_fg": "#ffffff",
        "list_select": "#333333"
    },
    "Light": {
        "bg": "#fdfdfd",
        "fg": "#202124",
        "panel_bg": "#f0f0f0",
        "toolbar_bg": "#f0f0f0",
        "accent": "#0078d4",
        "entry_bg": "#ffffff",
        "entry_fg": "#202124",
        "list_bg": "#f0f0f0",
        "list_fg": "#202124",
        "list_select": "#e0e0e0"
    }
}

class ThemeManager:
    def __init__(self):
        self.current_theme_name = "Dark"
        self.colors = DEFAULT_THEMES["Dark"].copy()
        self.load_theme()

    def load_theme(self):
        if os.path.exists(THEME_FILE):
            try:
                with open(THEME_FILE, "r") as f:
                    data = json.load(f)
                    self.current_theme_name = data.get("name", "Dark")
                    self.colors = data.get("colors", DEFAULT_THEMES["Dark"])
            except Exception:
                pass

    def save_theme(self):
        data = {
            "name": self.current_theme_name,
            "colors": self.colors
        }
        with open(THEME_FILE, "w") as f:
            json.dump(data, f)

    def set_theme(self, theme_name):
        if theme_name in DEFAULT_THEMES:
            self.current_theme_name = theme_name
            self.colors = DEFAULT_THEMES[theme_name].copy()
            self.save_theme()

    def get_color(self, key):
        return self.colors.get(key, "#000000")
