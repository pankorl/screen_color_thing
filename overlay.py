import tkinter as tk
import numpy as np

class Overlay():
    def __init__(self, width, height):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.configure(bg='black')
        self.root.title("Cluster Colors")
        self.window_height = height
        self.window_width = width
        self.root.geometry(f"{width}x{height}")  # Set the window size to be big enough to hold all partitions
        # Bind the click and drag events
        self.root.bind('<Button-1>', self.on_click)
        self.root.bind('<B1-Motion>', self.on_drag)
        self.root.attributes('-topmost', True)
        self.canvas = tk.Canvas(self.root, width=self.window_width, height=self.window_height)
        self.canvas.pack()

    def clear(self):
        self.canvas.delete("all")

    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.click_x
        y = self.root.winfo_y() + event.y - self.click_y
        self.root.geometry(f"+{x}+{y}")

    def on_click(self, event):
        self.click_x = event.x
        self.click_y = event.y
    
    def calc_positions(self, partitions):
        self.positions = []
        if partitions[0] == None:
            partitions = [[[0,1],[0,1]]]
        for partition in partitions:
            left = partition[0][0] * self.window_width
            top = partition[1][0] * self.window_height
            right = partition[0][1] * self.window_width
            bottom = partition[1][1] * self.window_height
            self.positions.append([left, top, right, bottom])

    def draw_partitions(self, partitions, colors):
        self.calc_positions(partitions)
        
        for j, _ in enumerate(partitions):
            position = self.positions[j]
            left, top, right, bottom = position
            this_colors = colors[j]
            for i, color in enumerate(this_colors):
                if isinstance(color, np.ndarray) and color.ndim > 1:
                    color = color.flatten()
                if isinstance(color, str):
                    color_hex = color
                else:
                    color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
                color_height =  (bottom-top) / len(this_colors)
                color_top = top + (i * color_height)
                color_bottom = top + ((i + 1) * color_height)
                self.canvas.create_rectangle(left, color_top, right, color_bottom, fill=color_hex, outline=color_hex)
        self.update_window()

    def update_window(self):
        self.root.update_idletasks()
        self.root.update()