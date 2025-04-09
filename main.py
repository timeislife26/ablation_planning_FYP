import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog


class TumorPlanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Tumour Planner")
        self.root.geometry("600x400")

        self.name_frame = tk.Frame(self.root)
        self.name_frame.pack(pady=5)
        self.model_name_label = tk.Label(self.name_frame, text="Model Name").grid(row=0, column=0)

        self.model_name_entry = tk.Entry(self.name_frame)
        self.model_name_entry.grid(row=0, column=1)
        self.name_frame.pack(pady=10)

        self.model_name_entry.insert(0, "Patient")

        self.tumor_entries = []
        self.create_input_fields()

        self.add_button = tk.Button(self.root, text="Add More Dimensions", command=self.create_input_fields)
        self.add_button.pack(pady=5)

        self.create_button = tk.Button(self.root, text="Create Tumour", command=self.on_create_tumour_click)
        self.create_button.pack(pady=10)

        self.create_button = tk.Button(self.root, text="Load Tumour", command=self.on_load_tumour_click)
        self.create_button.pack(pady=10)

        self.close_button = tk.Button(self.root, text="Close", command=self.root.destroy)
        self.close_button.pack(pady=10)

        self.load_dicom_button = tk.Button(self.root, text="Load DICOM Folder", command=self.on_load_dicom_click)
        self.load_dicom_button.pack(pady=10)

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

    def on_create_tumour_click(self):
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

        model_name = self.model_name_entry.get()
        # Pass tumors as a single string argument
        subprocess.run(["python", "Slicer_Script.py", "create", str(model_name),"|".join(tumor_data)])
        self.root.destroy()

    def on_load_tumour_click(self):
        """Loads the tumour from an obj file into 3D Slicer"""
        file_path = filedialog.askopenfilename(filetypes=[("OBJ Files", "*.obj")])
        subprocess.run(["python", "Slicer_Script.py", "import", file_path])
        self.root.destroy()

    def on_load_dicom_click(self):
        """Loads a DICOM folder into 3D Slicer"""
        folder_path = filedialog.askdirectory(title="Select DICOM Folder")
        if folder_path:
            subprocess.run(["python", "Slicer_Script.py", "dicom", folder_path])
            self.root.destroy()


if __name__ == "__main__":
    TumorPlanner()
