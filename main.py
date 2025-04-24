import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class TumorPlanner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Tumour Planner")
        self.root.geometry("635x500")

        # Apply modern theme and color enhancements
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure("TButton", padding=6, background="#d9e4f5", relief="flat")
        style.configure("TLabel", padding=4, background="#e8f0fe")
        style.configure("TLabelframe", background="#e8f0fe", relief="solid")
        style.configure("TLabelframe.Label", background="#bcd4ec", foreground="#2b2b2b", font=('Segoe UI', 10, 'bold'))

        self.tab_control = ttk.Notebook(self.root)

        self.dim_tab = tk.Frame(self.tab_control, bg="#f3f7fb")
        self.load_tab = tk.Frame(self.tab_control, bg="#f3f7fb")
        self.dicom_tab = tk.Frame(self.tab_control, bg="#f3f7fb")
        self.nifti_tab = tk.Frame(self.tab_control, bg="#f3f7fb")

        self.tab_control.add(self.dim_tab, text='Dimensions')
        self.tab_control.add(self.load_tab, text='Load')
        self.tab_control.add(self.dicom_tab, text='DICOM')
        self.tab_control.add(self.nifti_tab, text='NIfTI')
        self.tab_control.pack(expand=1, fill="both")

        self.tumor_entries = []

        self.init_dimensions_tab()
        self.init_load_tab()
        self.init_dicom_tab()
        self.init_nifti_tab()

        self.root.mainloop()

    def init_dimensions_tab(self):
        name_frame = ttk.LabelFrame(self.dim_tab, text="Model Name")
        name_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(name_frame, text="Model Name:").grid(row=0, column=0, padx=5, pady=5)
        self.model_name_entry = ttk.Entry(name_frame)
        self.model_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.model_name_entry.insert(0, "Patient")

        container = ttk.Frame(self.dim_tab)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, background="#f8fbff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.entries_frame = ttk.Frame(canvas)

        self.entries_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"), width=e.width)
        )

        canvas.create_window((0, 0), window=self.entries_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_input_fields()

        ttk.Button(self.dim_tab, text="Add More Dimensions", command=self.create_input_fields).pack(pady=5)
        ttk.Button(self.dim_tab, text="Create Tumour", command=self.on_create_tumour_click).pack(pady=5)

    def init_load_tab(self):
        ttk.Label(self.load_tab, text="Load an existing tumour from OBJ file:", font=('Segoe UI', 11)).pack(pady=20)
        ttk.Button(self.load_tab, text="Load Tumour", command=self.on_load_tumour_click).pack(pady=10)

    def init_dicom_tab(self):
        ttk.Label(self.dicom_tab, text="Load DICOM Folder into 3D Slicer:", font=('Segoe UI', 11)).pack(pady=20)
        ttk.Button(self.dicom_tab, text="Load DICOM Folder", command=self.on_load_dicom_click).pack(pady=10)

    def init_nifti_tab(self):
        ttk.Label(self.nifti_tab, text="Load NIfTI File into 3D Slicer:", font=('Segoe UI', 11)).pack(pady=20)
        ttk.Button(self.nifti_tab, text="Load NIfTI File", command=self.on_load_nifti_click).pack(pady=10)

    def create_input_fields(self):
        group = ttk.LabelFrame(self.entries_frame, text=f"Tumour Section {len(self.tumor_entries) + 1}")
        group.pack(fill="x", padx=5, pady=5, expand=True)

        for col in (1, 3, 5):
            group.columnconfigure(col, weight=1)

        labels = ["X Dim:", "Y Dim:", "Z Dim:", "X Pos:", "Y Pos:", "Z Pos:"]
        entries = []

        for i, label in enumerate(labels):
            ttk.Label(group, text=label).grid(row=i // 3, column=(i % 3) * 2, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(group)
            entry.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5, sticky='we')
            entries.append(entry)

        self.tumor_entries.append(entries)

    def on_create_tumour_click(self):
        tumor_data = []
        for entries in self.tumor_entries:
            try:
                values = [float(e.get()) for e in entries]
                if min(values[:3]) <= 0:
                    raise ValueError("Dimensions must be positive")
                tumor_data.append(",".join(map(str, values)))
            except ValueError:
                messagebox.showerror("Invalid Input", "Enter valid numbers for all fields.")
                return

        model_name = self.model_name_entry.get()
        subprocess.run(["python", "Slicer_Script.py", "create", model_name, "|".join(tumor_data)])
        self.root.destroy()

    def on_load_tumour_click(self):
        file_path = filedialog.askopenfilename(filetypes=[("OBJ Files", "*.obj")])
        if file_path:
            subprocess.run(["python", "Slicer_Script.py", "import", file_path])
            self.root.destroy()

    def on_load_dicom_click(self):
        folder_path = filedialog.askdirectory(title="Select DICOM Folder")
        if folder_path:
            subprocess.run(["python", "Slicer_Script.py", "dicom", folder_path])
            self.root.destroy()

    def on_load_nifti_click(self):
        file_path = filedialog.askopenfilename(filetypes=[("NIfTI Files", "*.nii *.nii.gz")])
        if file_path:
            subprocess.run(["python", "Slicer_Script.py", "nifti", file_path])
            self.root.destroy()

if __name__ == "__main__":
    TumorPlanner()
