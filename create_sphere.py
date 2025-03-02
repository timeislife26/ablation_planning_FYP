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

        label = QLabel("Modify your object. Click below when ready to save and continue.")
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


def create_sphere(radius):
    """Create a sphere with a user-defined radius and load it into Slicer."""
    global model_node  # So we can access it later when saving

    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(radius)
    sphere_source.SetThetaResolution(64)  # Increased resolution
    sphere_source.SetPhiResolution(64)
    sphere_source.Update()

    # Add the sphere to Slicer
    model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Sphere")
    model_node.SetAndObservePolyData(sphere_source.GetOutput())

    # Set display properties
    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    model_node.SetAndObserveDisplayNodeID(display_node.GetID())
    display_node.SetColor(1.0, 0.0, 0.0)
    display_node.SetOpacity(0.9)  # Reduce transparency

    print(f"Sphere with radius {radius} created in Slicer.")
    print("Modify the object as needed. Click 'Save and Continue' when ready.")

    # Open the floating UI that does not block Slicer
    SaveDialog()


def save_model_as_obj(model_name="Sphere"):
    """Apply transformations (if any) and save the model as an OBJ file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_folder = os.path.join(script_dir, "Obj_files")
    os.makedirs(obj_folder, exist_ok=True)

    save_path = os.path.join(obj_folder, "sphere.obj")

    model_node = slicer.util.getNode(model_name)
    if not model_node:
        print(f"Error: No model named '{model_name}' found in the scene.")
        return False

    # Check if the model has a transform applied
    transform_node = model_node.GetParentTransformNode()
    if transform_node:
        print("Applying transform before saving...")
        slicer.vtkSlicerTransformLogic().hardenTransform(model_node)

    # Save the model
    success = slicer.util.saveNode(model_node, save_path)
    if success:
        print(f"Model saved successfully to {save_path}")
        return True
    else:
        print("Failed to save model.")
        return False



def open_unity_project(project_path):
    unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe"
    execute_method = "ImportObj.ImportObjFile"

    cmd = f'"{unity_executable}" -projectPath "{project_path}" -executeMethod {execute_method}'
    print(f"Launching Unity project at {project_path} with method {execute_method}...")

    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Failed to launch Unity project: {e}")


def save_and_continue():
    """Manually save the object and open Unity when ready."""
    if save_model_as_obj("Sphere"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        unity_project_dir = os.path.join(script_dir, "Unity", "FYP_Testing")
        open_unity_project(unity_project_dir)
    else:
        print("Model was not saved. Fix any issues before continuing.")


# Check if a radius value is provided
if len(sys.argv) < 2:
    print("Usage: create_sphere.py <radius>")
    sys.exit(1)

# Convert the argument to a float, create the sphere, but DO NOT save immediately
try:
    user_radius = float(sys.argv[1])
    create_sphere(user_radius)

    print("\n>>> The object has been created in Slicer. Modify it as needed.")
    print(">>> A floating window will appear. Click 'Save and Continue' when ready.")

except ValueError:
    print("Invalid radius value. Please enter a valid number.")
    sys.exit(1)
