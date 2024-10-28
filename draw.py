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

        # Create canvas with specified width and height
        self.canvas = tk.Canvas(master, width=self.cols * col_width, height=self.rows * row_height)
        self.canvas.pack()

        # Draw the initial grid
        self.draw_grid()

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
                # Outline color set to white
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='white', tags=f"{row}_{col}")

        # Bind click events after drawing the grid
        self.canvas.bind("<Button-1>", self.change_color)  # Left click to change color
        self.canvas.bind("<Button-2>", self.print_matrix)    # Right click to print color

    def change_color(self, event):
        """Changes the color of the clicked block."""
        # Get the coordinates of the block
        col = event.x // col_width
        row = event.y // row_height

        # Ensure the click is within the grid limits
        if 0 <= col < self.cols and 0 <= row < self.rows:
            # Open color picker dialog
            color = colorchooser.askcolor(title="Choose a color")

            if color[0] is not None:
                r, g, b = [int(c) for c in color[0]]
                self.color_matrix[row][col] = [r, g, b]
                self.draw_grid()  # Redraw the grid with new colors

    def print_color(self, event):
        """Prints the RGB values of the clicked block."""
        # Get the coordinates of the block
        col = event.x // col_width
        row = event.y // row_height

        # Ensure the click is within the grid limits
        if 0 <= col < self.cols and 0 <= row < self.rows:
            rgb_values = self.color_matrix[row][col]
            print(f"Block ({row}, {col}) color: RGB {rgb_values}")
        else:
            print("Click was outside the matrix bounds.")

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
