import tkinter as tk
from PIL import Image, ImageTk
import webbrowser
import os

class FileViewer:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        # Create a scrollbar
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a canvas
        self.canvas = tk.Canvas(self.frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbar
        self.scrollbar.config(command=self.canvas.yview)

        # Bind the canvas to the mouse wheel
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)

        # Create a frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

    def load_image(self, file_path):
        # Load the image
        image = Image.open(file_path)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        label = tk.Label(self.inner_frame, image=photo)
        label.image = photo
        label.pack()

    def load_document(self, file_path):
        # Open the document in the default application
        webbrowser.open_new_tab(file_path)

    def load_media(self, file_path):
        # Open the media file in a media player
        os.startfile(file_path)

    def on_mousewheel(self, event):
        # Scroll the canvas when the mouse wheel is used
        self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')