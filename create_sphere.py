import sys
import vtk
import slicer

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

# Check if a radius value is provided
if len(sys.argv) < 2:
    print("Usage: create_sphere.py <radius>")
    sys.exit(1)

# Convert the argument to a float and create the sphere
try:
    user_radius = float(sys.argv[1])
    create_sphere(user_radius)
except ValueError:
    print("Invalid radius value. Please enter a valid number.")
    sys.exit(1)
