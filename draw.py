import tkinter as tk
from tkinter import colorchooser

class RGBMatrixApp:
    def __init__(self, master):
        self.master = master
        self.master.title("RGB LED Matrix")

        # Matrix dimensions
        self.rows = 11
        self.cols = 53

        # Initialize color matrix (black)
        self.color_matrix = [[[0, 0, 0] for _ in range(self.cols)] for _ in range(self.rows)]

        # Current color for coloring
        self.current_color = [255, 255, 255]  # Default to white

        # Flag to track if dragging
        self.dragging = False

        # Create canvas with specified width and height
        self.canvas = tk.Canvas(master, width=self.cols * col_width, height=self.rows * row_height)
        self.canvas.pack()

        # Draw the initial grid
        self.draw_grid()

        # Bind events
        self.canvas.bind("<Button-1>", self.start_click)  # Left click to set color (single click)
        self.canvas.bind("<B1-Motion>", self.drag_color)  # Dragging with left button
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)  # Stop dragging
        self.canvas.bind("<Button-3>", self.clear_block)  # Right click to clear block
        self.canvas.bind("<Button-2>", self.print_matrix)  # Middle click to print matrix

    def draw_grid(self):
        """Draws the grid on the canvas."""
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = col * col_width
                y1 = row * row_height
                x2 = x1 + col_width
                y2 = y1 + row_height

                # Fill with the current RGB color
                color = f'#{self.color_matrix[row][col][0]:02x}{self.color_matrix[row][col][1]:02x}{self.color_matrix[row][col][2]:02x}'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='white', tags=f"{row}_{col}")

    def start_click(self, event):
        """Handles the start of a left click."""
        self.dragging = False  # Reset dragging flag

    def drag_color(self, event):
        """Colors blocks while dragging."""
        self.dragging = True  # User is dragging
        self.color_block(event, self.current_color)

    def end_drag(self, event):
        """Handles the end of a left-click event (detect single click)."""
        if not self.dragging:  # If the user didn’t drag, show the color picker
            color = colorchooser.askcolor(title="Choose a color")
            if color[0] is not None:
                self.current_color = [int(c) for c in color[0]]  # Update the current color

    def clear_block(self, event):
        """Clears the block (sets it to black) where the right click occurs."""
        self.color_block(event, [0, 0, 0])

    def color_block(self, event, color):
        """Colors a single block based on the event coordinates."""
        # Get the coordinates of the block
        col = event.x // col_width
        row = event.y // row_height

        # Ensure the event is within the grid limits
        if 0 <= col < self.cols and 0 <= row < self.rows:
            # Update the color matrix
            self.color_matrix[row][col] = color

            # Update the grid with the new color
            x1 = col * col_width
            y1 = row * row_height
            x2 = x1 + col_width
            y2 = y1 + row_height
            hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline='white', tags=f"{row}_{col}")

    def print_matrix(self, event):
        """Prints the entire RGB matrix in a list of lists format."""
        output = "[\n"
        for row in self.color_matrix:
            output += "  [" + ", ".join([str(pixel) for pixel in row]) + "],\n"
        output += "]"

        print(output)

# Dimensions for the blocks (doubled size)
col_width = 30  # Was 15
row_height = 30  # Was 15

if __name__ == "__main__":
    root = tk.Tk()
    app = RGBMatrixApp(root)
    root.mainloop()
