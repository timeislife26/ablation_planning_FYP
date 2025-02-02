import subprocess
import os
import tkinter as tk
from tkinter import messagebox





def Start_Slicer(slicer_executable, radius):
    if os.path.exists(slicer_executable):
        try:
            # Launch 3D Slicer
            #subprocess.Popen([slicer_executable])
            print("3D Slicer is starting...")
            sphere_script_path = r"create_sphere.py"
            subprocess.run([
                slicer_executable,
                "--no-splash",
                "--python-script", sphere_script_path,
                str(radius)  # Pass radius as a string argument
            ])
        except Exception as e:
            print(f"Error while launching 3D Slicer: {e}")
    else:
        print(f"Slicer executable not found at {slicer_executable}")


def on_button_click():
    """Gets the user input, validates it, and starts Slicer."""
    try:
        radius = float(radius_entry.get())
        if radius <= 0:
            messagebox.showerror("Invalid Input", "Radius must be a positive number.")
            return
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")
        return

    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"

    Start_Slicer(slicer_executable, radius)



root = tk.Tk()
root.title("3D Tumour Planner")
root.geometry("300x150")

# Label for radius input
radius_label = tk.Label(root, text="Enter dimensions 1:")
radius_label.pack(pady=5)

# Entry field for radius
radius_entry = tk.Entry(root)
radius_entry.pack(pady=5)

create_button = tk.Button(root, text="Open 3D Slicer", command=on_button_click)
create_button.pack(pady=10)

# Run the GUI
root.mainloop()
