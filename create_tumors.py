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


def create_tumor(x_radius, y_radius, z_radius, x_pos, y_pos, z_pos, index):
    """Create an ellipsoid (tumor-like shape) at a specific position in Slicer."""
    tumor_source = vtk.vtkParametricEllipsoid()
    tumor_source.SetXRadius(x_radius)
    tumor_source.SetYRadius(y_radius)
    tumor_source.SetZRadius(z_radius)

    parametric_function_source = vtk.vtkParametricFunctionSource()
    parametric_function_source.SetParametricFunction(tumor_source)
    parametric_function_source.Update()

    model_name = f"Tumor_{index}"
    model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", model_name)
    model_node.SetAndObservePolyData(parametric_function_source.GetOutput())

    # Ensure a display node is created and enabled
    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    model_node.SetAndObserveDisplayNodeID(display_node.GetID())

    # Make sure visibility is ON
    display_node.SetVisibility(True)
    display_node.SetColor(0.8, 0.2, 0.2)  # Tumor color (dark red)
    display_node.SetOpacity(0.9)  # Semi-transparent

    # Move tumor to the correct position
    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLinearTransformNode")
    matrix = vtk.vtkMatrix4x4()
    matrix.SetElement(0, 3, x_pos)
    matrix.SetElement(1, 3, y_pos)
    matrix.SetElement(2, 3, z_pos)
    transform_node.SetMatrixTransformToParent(matrix)

    model_node.SetAndObserveTransformNodeID(transform_node.GetID())

    # Apply the transformation to lock the position
    slicer.vtkSlicerTransformLogic().hardenTransform(model_node)

    print(f"Tumor {index} created at ({x_pos}, {y_pos}, {z_pos}) with size ({x_radius}, {y_radius}, {z_radius})")


def save_and_continue():
    """Merge all tumors into one model and save as a single OBJ file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_folder = os.path.join(script_dir, "Obj_files")
    os.makedirs(obj_folder, exist_ok=True)
    file_name = model_name + ".obj"
    save_path = os.path.join(obj_folder, file_name)

    # Get all tumor nodes
    tumor_nodes = [node for node in slicer.util.getNodesByClass("vtkMRMLModelNode") if "Tumor_" in node.GetName()]

    if not tumor_nodes:
        print("No tumors found to save.")
        return

    # Create an append filter to merge all tumors
    append_filter = vtk.vtkAppendPolyData()

    for tumor_node in tumor_nodes:
        # Apply transformation before merging
        transform_node = tumor_node.GetParentTransformNode()
        if transform_node:
            slicer.vtkSlicerTransformLogic().hardenTransform(tumor_node)

        poly_data = tumor_node.GetPolyData()
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

# Read tumor data from Slicer script
if len(sys.argv) < 2:
    print("Usage: create_tumors.py <tumor_data>")
    sys.exit(1)

global model_name
arguments = sys.argv[1]
model_name = arguments.split("~")[0]
tumor_data = arguments.split("~")[1]
tumor_parts = tumor_data.split("|")

# Create each tumor
for index, part in enumerate(tumor_parts):
    x_dim, y_dim, z_dim, x_pos, y_pos, z_pos = map(float, part.split(","))
    create_tumor(x_dim, y_dim, z_dim, x_pos, y_pos, z_pos, index)

print("All tumors created. Modify as needed in Slicer.")
SaveDialog()
