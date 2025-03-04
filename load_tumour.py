import sys
import vtk
import slicer
import os
import subprocess
from qt import QWidget, QPushButton, QVBoxLayout, QLabel, Qt


class SaveDialog(QWidget):
    """A non-blocking floating window with a 'Save and Continue' button."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save and Continue")
        self.setGeometry(100, 100, 300, 100)  # Position and size
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Window)  # Always on top, non-blocking

        layout = QVBoxLayout()

        label = QLabel("Modify your tumors. Click below when ready to save and continue.")
        layout.addWidget(label)

        self.save_button = QPushButton("Save and Continue")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.show()  # Show window without blocking Slicer

    def on_save(self):
        """Trigger save and close window."""
        save_and_continue()
        self.close()  # Close this window after saving


def load_tumour(file_path):
    print("Trying to load Model")
    slicer.util.loadModel(file_path)


def save_and_continue():
    """Merge all tumors into one model and save as a single OBJ file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_folder = os.path.join(script_dir, "Obj_files")
    os.makedirs(obj_folder, exist_ok=True)
    save_path = os.path.join(obj_folder, "tumour.obj")

    all_models = slicer.util.getNodesByClass("vtkMRMLModelNode")

    # Print their names
    for model in all_models:
        print(model.GetName())
    # Values in the models that I don't want to merge
    ignore_fields = ["Red Volume Slice", "Green Volume Slice", "Yellow Volume Slice"]
    # Create an append filter to merge all tumors
    append_filter = vtk.vtkAppendPolyData()

    for model in all_models:
        if model.GetName() not in ignore_fields: # Must look if ther is a better way
            # Apply transformation before merging
            transform_node = model.GetParentTransformNode()
            if transform_node:
                slicer.vtkSlicerTransformLogic().hardenTransform(model)

            poly_data = model.GetPolyData()
            if poly_data:
                append_filter.AddInputData(poly_data)

    append_filter.Update()

    # Create a new merged model
    merged_model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Merged_Tumor_Model")
    merged_model_node.SetAndObservePolyData(append_filter.GetOutput())

    # Assign a display node to ensure visibility
    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    merged_model_node.SetAndObserveDisplayNodeID(display_node.GetID())
    display_node.SetVisibility(True)
    display_node.SetColor(0.8, 0.2, 0.2)  # Tumor color (dark red)
    display_node.SetOpacity(0.9)  # Semi-transparent

    # Save the merged model as a single OBJ file
    success = slicer.util.saveNode(merged_model_node, save_path)

    if success:
        print(f"Project saved successfully as {save_path}")
    else:
        print("Failed to save project.")

    print("Opening Unity...")
    open_unity_project(os.path.join(script_dir, "Unity", "FYP_Testing"), save_path)


def open_unity_project(project_path, save_path):
    unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe"
    execute_method = "ImportObj.ImportObjFile"

    # Add --filePath as an argument
    cmd = f'"{unity_executable}" -projectPath "{project_path}" -executeMethod {execute_method} --filePath "{save_path}"'

    print(f"Launching Unity project at {project_path} with method {execute_method} and file {save_path}...")

    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Failed to launch Unity project: {e}")


# Read file path of obj file from Slicer script
if len(sys.argv) < 2:
    print("Usage: create_tumors.py <tumor_data>")
    sys.exit(1)

file_path = sys.argv[1]
load_tumour(file_path)
print("Tumour loaded successfully")
SaveDialog()