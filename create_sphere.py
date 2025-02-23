import sys
import vtk
import slicer
import os
import subprocess


def create_sphere(radius):
    """Create a sphere with a user-defined radius and load it into Slicer."""
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(radius)
    sphere_source.SetThetaResolution(32)
    sphere_source.SetPhiResolution(32)
    sphere_source.Update()

    # Add the sphere to Slicer
    model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Sphere")
    model_node.SetAndObservePolyData(sphere_source.GetOutput())

    # Set display properties
    display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
    model_node.SetAndObserveDisplayNodeID(display_node.GetID())
    display_node.SetColor(0.0, 1.0, 0.0)  # Green color
    display_node.SetOpacity(0.7)  # Slight transparency

    print(f"Sphere with radius {radius} created in Slicer.")


def save_model_as_obj(model_name="Sphere"):
    """Save the created model as an OBJ file in the Obj_files directory."""
    # Get the script's directory and create Obj_files folder if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_folder = os.path.join(script_dir, "Obj_files")
    os.makedirs(obj_folder, exist_ok=True)

    # Define the full save path
    save_path = os.path.join(obj_folder, "sphere.obj")

    model_node = slicer.util.getNode(model_name)
    if not model_node:
        print(f"Error: No model named '{model_name}' found in the scene.")
        return False

    # Save the model to the specified path
    success = slicer.util.saveNode(model_node, save_path)
    if success:
        print(f"Model saved successfully to {save_path}")
        return True
    else:
        print("Failed to save model.")
        return False


def open_unity_project(project_path):
    # Update this path to the location of your Unity Editor executable.
    unity_executable = r"C:\Program Files\Unity\Hub\Editor\2022.3.15f1\Editor\Unity.exe"

    execute_method = "ImportObj.ImportObjFile"

    # Construct the command to open the Unity project and execute the import script
    cmd = f'"{unity_executable}" -projectPath "{project_path}" -executeMethod {execute_method}'
    print(f"Launching Unity project at {project_path} with method {execute_method}...")

    try:
        subprocess.Popen(cmd, shell=True)
    except Exception as e:
        print(f"Failed to launch Unity project: {e}")



# Check if a radius value is provided
if len(sys.argv) < 2:
    print("Usage: create_sphere.py <radius>")
    sys.exit(1)

# Convert the argument to a float, create the sphere, save it, and then open Unity project
try:
    user_radius = float(sys.argv[1])
    create_sphere(user_radius)

    if save_model_as_obj("Sphere"):
        # Get the directory where the script is stored.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Finds the unity project from this directory and opens it
        unity_project_dir = os.path.join(script_dir, "Unity", "FYP_Testing")
        open_unity_project(unity_project_dir)
except ValueError:
    print("Invalid radius value. Please enter a valid number.")
    sys.exit(1)
