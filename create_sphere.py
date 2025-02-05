import sys
import vtk
import slicer
import os

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
    os.makedirs(obj_folder, exist_ok=True)  # Create folder if it doesn’t exist

    # Define the full save path
    save_path = os.path.join(obj_folder, "sphere.obj")

    model_node = slicer.util.getNode(model_name)

    if not model_node:
        print(f"Error: No model named '{model_name}' found in the scene.")
        return

    # Save the model to the specified path
    success = slicer.util.saveNode(model_node, save_path)

    if success:
        print(f"Model saved successfully to {save_path}")
    else:
        print("Failed to save model.")

# Check if a radius value is provided
if len(sys.argv) < 2:
    print("Usage: create_sphere.py <radius>")
    sys.exit(1)

# Convert the argument to a float and create the sphere
try:
    user_radius = float(sys.argv[1])
    create_sphere(user_radius)
    save_model_as_obj("Sphere")
except ValueError:
    print("Invalid radius value. Please enter a valid number.")
    sys.exit(1)
