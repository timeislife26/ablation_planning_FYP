import subprocess
import tkinter as tk
from tkinter import messagebox

#Class to show the starting GUI for the program
class Starting_Interface():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Tumour Planner")
        self.root.geometry("300x150")

        # Label for radius input
        self.radius_label = tk.Label(self.root, text="Enter dimensions 1:")
        self.radius_label.pack(pady=5)

        # Entry field for radius
        self.radius_entry = tk.Entry(self.root)
        self.radius_entry.pack(pady=5)

        # Buttons to open 3D slicer program or close GUI
        self.create_button = tk.Button(self.root, text="Open 3D Slicer", command=lambda :self.on_button_click())
        self.create_button.pack(pady=10)
        self.close_button = tk.Button(self.root, text="Close", command=lambda : self.root.destroy())
        self.close_button.pack(pady=10)

        # Run the GUI
        self.root.mainloop()

    def on_button_click(self):
        """Gets the user input, validates it, and starts Slicer."""
        try:
            radius = float(self.radius_entry.get())
            if radius <= 0:
                messagebox.showerror("Invalid Input", "Radius must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

        subprocess.run(["python", "Slicer_Script.py", str(radius)])
        self.root.destroy() # Closes GUI

def main():
     Starting_Interface()


if __name__ == "__main__":
    main()