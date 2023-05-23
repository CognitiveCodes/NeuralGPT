import tkinter as tk
from tkinter import font

class ChatWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.title("Chat Window")
        self.parent.geometry("400x500")

        # Create a text box to display the conversation
        self.text_box = tk.Text(self.parent, wrap="word")
        self.text_box.pack(fill="both", expand=True)

        # Create a font menu
        self.font_menu = tk.Menu(self.parent, tearoff=0)
        self.font_size_menu = tk.Menu(self.font_menu, tearoff=0)
        self.font_style_menu = tk.Menu(self.font_menu, tearoff=0)

        # Populate the font size menu
        font_sizes = [8, 10, 12, 14, 16, 18, 20]
        for size in font_sizes:
            self.font_size_menu.add_command(label=str(size), command=lambda s=size: self.set_font_size(s))
        self.font_menu.add_cascade(label="Size", menu=self.font_size_menu)

        # Populate the font style menu
        font_styles = ["normal", "bold", "italic", "underline"]
        for style in font_styles:
            self.font_style_menu.add_command(label=style, command=lambda s=style: self.set_font_style(s))
        self.font_menu.add_cascade(label="Style", menu=self.font_style_menu)

        # Create a font button to activate the font menu
        self.font_button = tk.Button(self.parent, text="Font", command=self.show_font_menu)
        self.font_button.pack(side="right")

    def show_font_menu(self):
        # Display the font menu
        self.font_menu.post(self.font_button.winfo_rootx(), self.font_button.winfo_rooty())

    def set_font_size(self, size):
        # Set the font size of the text box
        current_font = font.Font(font=self.text_box["font"])
        self.text_box.configure(font=(current_font.actual()["family"], size))

    def set_font_style(self, style):
        # Set the font style of the text box
        current_font = font.Font(font=self.text_box["font"])
        if style == "normal":
            self.text_box.configure(font=(current_font.actual()["family"], current_font.actual()["size"]))
        else:
            self.text_box.configure(font=(current_font.actual()["family"], current_font.actual()["size"], style))

if __name__ == "__main__":
    root = tk.Tk()
    chat_window = ChatWindow(root)
    chat_window.pack(fill="both", expand=True)
    root.mainloop()