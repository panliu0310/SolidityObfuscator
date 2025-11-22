import json

from tkinter import messagebox

class config:
    def __init__(self, _config_file_path):
        self.config_file_path = _config_file_path
        try:
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                self.config = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration file:\n{e}")
            return
        
    def load_config(self):
        return json.loads(self.config)

    def save_config(self, dict):
        try:
            with open(self.config_file_path, "w") as json_file:
                json.dump(dict, json_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration file:\n{e}")
            return