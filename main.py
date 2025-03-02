import subprocess
import tkinter as tk
from tkinter import messagebox


class TumorPlanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Tumour Planner")
        self.root.geometry("400x400")

        self.tumor_entries = []
        self.create_input_fields()

        self.add_button = tk.Button(self.root, text="Add Another Tumour", command=self.create_input_fields)
        self.add_button.pack(pady=5)

        self.create_button = tk.Button(self.root, text="Open 3D Slicer", command=self.on_button_click)
        self.create_button.pack(pady=10)

        self.close_button = tk.Button(self.root, text="Close", command=self.root.destroy)
        self.close_button.pack(pady=10)

        self.root.mainloop()

    def create_input_fields(self):
        """Create input fields for a new tumor specification."""
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="X Dim:").grid(row=0, column=0)
        entry_x = tk.Entry(frame)
        entry_x.grid(row=0, column=1)

        tk.Label(frame, text="Y Dim:").grid(row=0, column=2)
        entry_y = tk.Entry(frame)
        entry_y.grid(row=0, column=3)

        tk.Label(frame, text="Z Dim:").grid(row=0, column=4)
        entry_z = tk.Entry(frame)
        entry_z.grid(row=0, column=5)

        tk.Label(frame, text="X Pos:").grid(row=1, column=0)
        entry_px = tk.Entry(frame)
        entry_px.grid(row=1, column=1)

        tk.Label(frame, text="Y Pos:").grid(row=1, column=2)
        entry_py = tk.Entry(frame)
        entry_py.grid(row=1, column=3)

        tk.Label(frame, text="Z Pos:").grid(row=1, column=4)
        entry_pz = tk.Entry(frame)
        entry_pz.grid(row=1, column=5)

        self.tumor_entries.append((entry_x, entry_y, entry_z, entry_px, entry_py, entry_pz))

    def on_button_click(self):
        """Get user inputs, validate them, and start Slicer."""
        tumor_data = []
        for entries in self.tumor_entries:
            try:
                x_dim = float(entries[0].get())
                y_dim = float(entries[1].get())
                z_dim = float(entries[2].get())
                x_pos = float(entries[3].get())
                y_pos = float(entries[4].get())
                z_pos = float(entries[5].get())

                if min(x_dim, y_dim, z_dim) <= 0:
                    raise ValueError("Dimensions must be positive")

                tumor_data.append(f"{x_dim},{y_dim},{z_dim},{x_pos},{y_pos},{z_pos}")

            except ValueError:
                messagebox.showerror("Invalid Input", "Enter valid numbers for all fields.")
                return

        # Pass tumors as a single string argument
        subprocess.run(["python", "Slicer_Script.py", "|".join(tumor_data)])
        self.root.destroy()


if __name__ == "__main__":
    TumorPlanner()
