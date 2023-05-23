import tkinter as tk

class GUIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal Embedding Framework")
        self.root.geometry("800x600")

        # Create menu bar
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open")
        self.file_menu.add_command(label="Save")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Cut")
        self.edit_menu.add_command(label="Copy")
        self.edit_menu.add_command(label="Paste")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Toggle Fullscreen")
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About")
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.root.config(menu=self.menu_bar)

        # Create text area for document editing
        self.text_area = tk.Text(self.root)
        self.text_area.pack(expand=True, fill="both")

        self.root.mainloop()

if __name__ == "__main__":
    gui_manager = GUIManager()