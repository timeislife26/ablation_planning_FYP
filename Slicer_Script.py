import subprocess
import os
import sys


def Start_Slicer(radius):
    slicer_executable = r"C:\Program Files\slicer.org\Slicer 5.8.0\Slicer.exe"
    if os.path.exists(slicer_executable):
        try:
            # Launch 3D Slicer
            print("3D Slicer is starting...")
            sphere_script_path = r"create_sphere.py"
            subprocess.Popen([
                slicer_executable,
                "--no-splash",
                "--python-script", sphere_script_path,
                str(radius)  # Pass radius as a string argument
            ])
        except Exception as e:
            print(f"Error while launching 3D Slicer: {e}")
    else:
        print(f"Slicer executable not found at {slicer_executable}")


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    # Convert the argument to a float and create the sphere
    try:
        user_radius = float(sys.argv[1])
        Start_Slicer(user_radius)
    except ValueError:
        print("Invalid radius value. Please enter a valid number.")
        sys.exit(1)

if __name__ == "__main__":
    main()